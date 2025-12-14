"""
Task 2: Supermarket Market Basket Analysis
"""

import csv
from collections import defaultdict

#DATA LOADING

def load_transactions(filename):
    """
    Load transaction data from CSV file
    Returns list of dictionaries
    """
    transactions = []
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                transactions.append(row)
        print(f"Loaded {len(transactions)} transactions")
        return transactions
    except FileNotFoundError:
        print(f"Error: File {filename} not found!")
        return []


#DATA STRUCTURE: GRAPH

class ItemGraph:
    """
    Graph data structure using adjacency list
    Represents items and their co-purchase relationships

    This is a simple implementation using dictionaries and lists
    (suitable for junior developer level)
    """

    def __init__(self):
        # Dictionary to store graph edges
        # Key: item name
        # Value: list of connected items (items bought together)
        self.graph = {}

        # Dictionary to count item frequencies
        self.item_count = {}

        # Dictionary to count edge weights (how often items bought together)
        self.edge_weight = {}

    def add_item(self, item):
        """
        Add an item (node) to the graph if it doesn't exist
        """
        if item not in self.graph:
            self.graph[item] = []  # Empty list of connections
            self.item_count[item] = 0

    def add_edge(self, item1, item2):
        """
        Add an edge between two items (they were bought together)
        """
        # Make sure both items exist in graph
        self.add_item(item1)
        self.add_item(item2)

        # Add connection (undirected graph - both directions)
        if item2 not in self.graph[item1]:
            self.graph[item1].append(item2)
        if item1 not in self.graph[item2]:
            self.graph[item2].append(item1)

        # Increment edge weight
        edge_key = tuple(sorted([item1, item2]))  # Sort to avoid duplicates
        if edge_key not in self.edge_weight:
            self.edge_weight[edge_key] = 0
        self.edge_weight[edge_key] += 1

    def increment_item_count(self, item):
        """
        Increase the count for an item (how many times it was purchased)
        """
        if item in self.item_count:
            self.item_count[item] += 1

    def get_neighbors(self, item):
        """
        Get all items connected to this item (bought together)
        """
        if item in self.graph:
            return self.graph[item]
        return []

    def get_total_items(self):
        """
        Get total number of unique items in graph
        """
        return len(self.graph)

    def get_total_edges(self):
        """
        Get total number of connections (co-purchase relationships)
        """
        return len(self.edge_weight)


#ALGORITHM: BUILD GRAPH FROM TRANSACTIONS

def build_graph_from_transactions(transactions):
    """
    Algorithm to build item graph from transaction data
    Groups transactions by member and date, then creates edges
    """
    graph = ItemGraph()

    # Step 1: Group transactions by member and date
    # Dictionary: key = (member_number, date), value = list of items
    baskets = {}

    for transaction in transactions:
        member = transaction['Member_number']
        date = transaction['Date']
        item = transaction['itemDescription']

        # Create basket key
        basket_key = (member, date)

        # Add item to basket
        if basket_key not in baskets:
            baskets[basket_key] = []
        baskets[basket_key].append(item)

    print(f"Found {len(baskets)} unique shopping baskets")

    # Step 2: Build graph from baskets
    for basket_items in baskets.values():
        # Add all items in basket to graph
        for item in basket_items:
            graph.add_item(item)
            graph.increment_item_count(item)

        # Create edges between all pairs of items in the basket
        for i in range(len(basket_items)):
            for j in range(i + 1, len(basket_items)):
                item1 = basket_items[i]
                item2 = basket_items[j]
                graph.add_edge(item1, item2)

    return graph


#ALGORITHM: FREQUENT ITEM PAIR ANALYSIS

def find_frequent_pairs(graph, min_support=5):
    """
    Find item pairs that are frequently bought together
    min_support: minimum number of times items must appear together
    """
    frequent_pairs = []

    # Sort edges by weight (frequency)
    sorted_edges = sorted(
        graph.edge_weight.items(),
        key=lambda x: x[1],
        reverse=True
    )

    # Filter by minimum support
    for edge, weight in sorted_edges:
        if weight >= min_support:
            item1, item2 = edge
            frequent_pairs.append({
                'item1': item1,
                'item2': item2,
                'frequency': weight
            })

    return frequent_pairs


def find_most_popular_items(graph, top_n=10):
    """
    Find the most frequently purchased items
    """
    # Sort items by count
    sorted_items = sorted(
        graph.item_count.items(),
        key=lambda x: x[1],
        reverse=True
    )

    # Return top N
    return sorted_items[:top_n]


def find_items_bought_with(graph, target_item):
    """
    Find what items are commonly bought with a specific item
    Returns list of (item, frequency) tuples
    """
    if target_item not in graph.graph:
        return []

    # Get neighbors
    neighbors = graph.get_neighbors(target_item)

    # Get frequency for each neighbor
    result = []
    for neighbor in neighbors:
        edge_key = tuple(sorted([target_item, neighbor]))
        frequency = graph.edge_weight.get(edge_key, 0)
        result.append((neighbor, frequency))

    # Sort by frequency
    result.sort(key=lambda x: x[1], reverse=True)

    return result


#VISUALIZATION (TEXT-BASED)

def visualize_item_connections(graph, item, max_connections=5):
    """
    Simple text-based visualization of item connections
    """
    if item not in graph.graph:
        print(f"Item '{item}' not found in graph")
        return

    neighbors = find_items_bought_with(graph, item)

    print(f"\n{'='*60}")
    print(f"Items frequently bought with: {item}")
    print(f"{'='*60}")
    print(f"Total purchase count: {graph.item_count[item]}")
    print(f"\nTop {max_connections} co-purchased items:")
    print(f"{'-'*60}")

    for i, (neighbor, freq) in enumerate(neighbors[:max_connections]):
        # Simple bar chart
        bar_length = int(freq / 2)  # Scale down for display
        bar = '█' * min(bar_length, 40)
        print(f"{i+1}. {neighbor:30s} │ {bar} ({freq})")

    print(f"{'='*60}\n")


def visualize_graph_structure(graph):
    """
    Display basic graph statistics
    """
    print(f"\n{'='*60}")
    print(f"  GRAPH STRUCTURE SUMMARY")
    print(f"{'='*60}")
    print(f"Total unique items (nodes):     {graph.get_total_items()}")
    print(f"Total co-purchase links (edges): {graph.get_total_edges()}")
    print(f"{'='*60}\n")


#DISPLAY FUNCTIONS

def display_frequent_pairs(pairs, limit=10):
    """
    Display frequent item pairs in a readable format
    """
    print(f"\n{'='*70}")
    print(f"  TOP {limit} FREQUENTLY CO-PURCHASED ITEM PAIRS")
    print(f"{'='*70}")
    print(f"{'Rank':<6} {'Item 1':<25} {'Item 2':<25} {'Frequency':<10}")
    print(f"{'-'*70}")

    for i, pair in enumerate(pairs[:limit]):
        print(f"{i+1:<6} {pair['item1']:<25} {pair['item2']:<25} {pair['frequency']:<10}")

    print(f"{'='*70}\n")


def display_popular_items(items, limit=10):
    """
    Display most popular items
    """
    print(f"\n{'='*60}")
    print(f"  TOP {limit} MOST POPULAR ITEMS")
    print(f"{'='*60}")
    print(f"{'Rank':<6} {'Item':<35} {'Purchase Count':<15}")
    print(f"{'-'*60}")

    for i, (item, count) in enumerate(items):
        print(f"{i+1:<6} {item:<35} {count:<15}")

    print(f"{'='*60}\n")


def show_menu():
    """
    Display menu options
    """
    print("\n" + "="*60)
    print("  SUPERMARKET MARKET BASKET ANALYSIS")
    print("  Graph-Based Item Association Analysis")
    print("="*60)
    print("1. Load Data and Build Graph")
    print("2. View Graph Statistics")
    print("3. Find Most Popular Items")
    print("4. Find Frequent Item Pairs")
    print("5. Analyze Specific Item (What's bought with it?)")
    print("6. Visualize Item Connections")
    print("0. Exit")
    print("="*60)


#MAIN PROGRAM

def main():
    """
    Main program
    """
    print("Welcome to Supermarket Market Basket Analysis!")
    print("Using Graph Data Structure for Item Association Mining")

    # Variable to store the graph
    item_graph = None

    while True:
        show_menu()
        choice = input("\nEnter your choice (0-6): ").strip()

        if choice == '1':
            # Load data and build graph
            print("\nLoading transaction data...")
            transactions = load_transactions('Supermarket_dataset_PAI.csv')

            if len(transactions) > 0:
                print("Building item graph...")
                item_graph = build_graph_from_transactions(transactions)
                print(f"\nGraph built successfully!")
                print(f"  - {item_graph.get_total_items()} unique items")
                print(f"  - {item_graph.get_total_edges()} co-purchase relationships")

        elif choice == '2':
            # View graph statistics
            if item_graph is None:
                print("Please load data first (option 1)")
            else:
                visualize_graph_structure(item_graph)

        elif choice == '3':
            # Most popular items
            if item_graph is None:
                print("Please load data first (option 1)")
            else:
                top_n = int(input("How many top items to show? (default 10): ") or 10)
                popular = find_most_popular_items(item_graph, top_n)
                display_popular_items(popular, top_n)

        elif choice == '4':
            # Frequent pairs
            if item_graph is None:
                print("Please load data first (option 1)")
            else:
                min_support = int(input("Minimum frequency (default 5): ") or 5)
                pairs = find_frequent_pairs(item_graph, min_support)

                limit = int(input("How many pairs to show? (default 10): ") or 10)
                display_frequent_pairs(pairs, limit)

                print(f"Total pairs with frequency >= {min_support}: {len(pairs)}")

        elif choice == '5':
            # Analyze specific item
            if item_graph is None:
                print("Please load data first (option 1)")
            else:
                item_name = input("Enter item name: ").strip()
                neighbors = find_items_bought_with(item_graph, item_name)

                if len(neighbors) == 0:
                    print(f"No data found for '{item_name}'")
                else:
                    print(f"\nItems bought with '{item_name}':")
                    print(f"Total purchase count: {item_graph.item_count[item_name]}")
                    print(f"\nTop 10 co-purchased items:")
                    for i, (neighbor, freq) in enumerate(neighbors[:10]):
                        print(f"  {i+1}. {neighbor} (bought together {freq} times)")

        elif choice == '6':
            # Visualize item connections
            if item_graph is None:
                print("Please load data first (option 1)")
            else:
                item_name = input("Enter item name: ").strip()
                max_conn = int(input("Max connections to show (default 5): ") or 5)
                visualize_item_connections(item_graph, item_name, max_conn)

        elif choice == '0':
            # Exit
            print("\nThank you for using the analysis tool. Goodbye!")
            break

        else:
            print("Invalid choice. Please try again.")


# Run the program
if __name__ == "__main__":
    main()
