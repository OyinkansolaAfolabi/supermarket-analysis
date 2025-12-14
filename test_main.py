"""
Test file for Task 2
"""

import unittest
from main import (
    ItemGraph,
    build_graph_from_transactions,
    find_frequent_pairs,
    find_most_popular_items,
    find_items_bought_with
)


class TestItemGraph(unittest.TestCase):
    """Test the ItemGraph data structure"""

    def setUp(self):
        """Create a test graph"""
        self.graph = ItemGraph()

    def test_add_item(self):
        """Test adding items to graph"""
        self.graph.add_item('milk')
        self.graph.add_item('bread')

        self.assertIn('milk', self.graph.graph)
        self.assertIn('bread', self.graph.graph)
        self.assertEqual(self.graph.get_total_items(), 2)

    def test_add_duplicate_item(self):
        """Test that adding duplicate items doesn't create duplicates"""
        self.graph.add_item('milk')
        self.graph.add_item('milk')

        self.assertEqual(self.graph.get_total_items(), 1)

    def test_add_edge(self):
        """Test adding edges between items"""
        self.graph.add_edge('milk', 'bread')

        # Check both items were added
        self.assertIn('milk', self.graph.graph)
        self.assertIn('bread', self.graph.graph)

        # Check connection exists (undirected graph)
        self.assertIn('bread', self.graph.get_neighbors('milk'))
        self.assertIn('milk', self.graph.get_neighbors('bread'))

    def test_edge_weight(self):
        """Test that edge weights are tracked correctly"""
        self.graph.add_edge('milk', 'bread')
        self.graph.add_edge('milk', 'bread')  # Add same edge again

        edge_key = tuple(sorted(['milk', 'bread']))
        self.assertEqual(self.graph.edge_weight[edge_key], 2)

    def test_increment_item_count(self):
        """Test item frequency counting"""
        self.graph.add_item('milk')
        self.graph.increment_item_count('milk')
        self.graph.increment_item_count('milk')
        self.graph.increment_item_count('milk')

        self.assertEqual(self.graph.item_count['milk'], 3)

    def test_get_neighbors_empty(self):
        """Test getting neighbors of non-existent item"""
        neighbors = self.graph.get_neighbors('nonexistent')
        self.assertEqual(len(neighbors), 0)

    def test_get_neighbors(self):
        """Test getting neighbors of an item"""
        self.graph.add_edge('milk', 'bread')
        self.graph.add_edge('milk', 'butter')
        self.graph.add_edge('milk', 'cheese')

        neighbors = self.graph.get_neighbors('milk')
        self.assertEqual(len(neighbors), 3)
        self.assertIn('bread', neighbors)
        self.assertIn('butter', neighbors)
        self.assertIn('cheese', neighbors)


class TestBuildGraph(unittest.TestCase):
    """Test building graph from transactions"""

    def setUp(self):
        """Create test transaction data"""
        self.test_transactions = [
            {'Member_number': '1', 'Date': '01-01-2015', 'itemDescription': 'milk'},
            {'Member_number': '1', 'Date': '01-01-2015', 'itemDescription': 'bread'},
            {'Member_number': '1', 'Date': '01-01-2015', 'itemDescription': 'butter'},
            {'Member_number': '2', 'Date': '02-01-2015', 'itemDescription': 'milk'},
            {'Member_number': '2', 'Date': '02-01-2015', 'itemDescription': 'bread'},
        ]

    def test_build_graph(self):
        """Test building graph from transactions"""
        graph = build_graph_from_transactions(self.test_transactions)

        # Should have 3 unique items
        self.assertEqual(graph.get_total_items(), 3)

        # Check items exist
        self.assertIn('milk', graph.graph)
        self.assertIn('bread', graph.graph)
        self.assertIn('butter', graph.graph)

    def test_item_frequencies(self):
        """Test that item frequencies are counted correctly"""
        graph = build_graph_from_transactions(self.test_transactions)

        # milk appears 2 times, bread 2 times, butter 1 time
        self.assertEqual(graph.item_count['milk'], 2)
        self.assertEqual(graph.item_count['bread'], 2)
        self.assertEqual(graph.item_count['butter'], 1)

    def test_edge_creation(self):
        """Test that edges are created between items in same basket"""
        graph = build_graph_from_transactions(self.test_transactions)

        # milk and bread were bought together twice
        edge_key = tuple(sorted(['milk', 'bread']))
        self.assertEqual(graph.edge_weight[edge_key], 2)

        # milk and butter bought together once
        edge_key2 = tuple(sorted(['milk', 'butter']))
        self.assertEqual(graph.edge_weight[edge_key2], 1)


class TestFrequentPairs(unittest.TestCase):
    """Test finding frequent item pairs"""

    def setUp(self):
        """Create a test graph with some data"""
        self.graph = ItemGraph()

        # Create edges
        for i in range(10):
            self.graph.add_edge('milk', 'bread')

        for i in range(5):
            self.graph.add_edge('milk', 'butter')

        for i in range(3):
            self.graph.add_edge('bread', 'cheese')

    def test_find_frequent_pairs(self):
        """Test finding pairs above minimum support"""
        pairs = find_frequent_pairs(self.graph, min_support=5)

        # Should find 2 pairs (milk-bread: 10, milk-butter: 5)
        self.assertEqual(len(pairs), 2)

    def test_find_frequent_pairs_sorting(self):
        """Test that pairs are sorted by frequency"""
        pairs = find_frequent_pairs(self.graph, min_support=3)

        # First pair should be milk-bread (10)
        self.assertEqual(pairs[0]['frequency'], 10)
        self.assertIn('milk', [pairs[0]['item1'], pairs[0]['item2']])
        self.assertIn('bread', [pairs[0]['item1'], pairs[0]['item2']])

    def test_find_frequent_pairs_min_support(self):
        """Test minimum support filtering"""
        pairs = find_frequent_pairs(self.graph, min_support=100)

        # No pairs should meet this high threshold
        self.assertEqual(len(pairs), 0)


class TestPopularItems(unittest.TestCase):
    """Test finding most popular items"""

    def setUp(self):
        """Create a test graph"""
        self.graph = ItemGraph()
        self.graph.add_item('milk')
        self.graph.add_item('bread')
        self.graph.add_item('butter')

        # Set counts
        self.graph.item_count['milk'] = 100
        self.graph.item_count['bread'] = 75
        self.graph.item_count['butter'] = 50

    def test_find_most_popular(self):
        """Test finding most popular items"""
        popular = find_most_popular_items(self.graph, top_n=3)

        self.assertEqual(len(popular), 3)

        # First should be milk (100)
        self.assertEqual(popular[0][0], 'milk')
        self.assertEqual(popular[0][1], 100)

    def test_find_most_popular_limit(self):
        """Test limiting number of results"""
        popular = find_most_popular_items(self.graph, top_n=2)

        self.assertEqual(len(popular), 2)
        # Should be milk and bread
        self.assertEqual(popular[0][0], 'milk')
        self.assertEqual(popular[1][0], 'bread')


class TestItemsBoughtWith(unittest.TestCase):
    """Test finding items bought with a specific item"""

    def setUp(self):
        """Create test graph"""
        self.graph = ItemGraph()

        # milk bought with bread 10 times
        for i in range(10):
            self.graph.add_edge('milk', 'bread')

        # milk bought with butter 5 times
        for i in range(5):
            self.graph.add_edge('milk', 'butter')

    def test_find_items_bought_with(self):
        """Test finding items bought with milk"""
        items = find_items_bought_with(self.graph, 'milk')

        self.assertEqual(len(items), 2)

        # Should be sorted by frequency
        self.assertEqual(items[0][0], 'bread')  # Most frequent
        self.assertEqual(items[0][1], 10)

    def test_find_items_bought_with_nonexistent(self):
        """Test with non-existent item"""
        items = find_items_bought_with(self.graph, 'nonexistent')
        self.assertEqual(len(items), 0)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases"""

    def test_empty_graph(self):
        """Test operations on empty graph"""
        graph = ItemGraph()

        self.assertEqual(graph.get_total_items(), 0)
        self.assertEqual(graph.get_total_edges(), 0)

    def test_single_item(self):
        """Test graph with single item (no edges)"""
        graph = ItemGraph()
        graph.add_item('milk')

        self.assertEqual(graph.get_total_items(), 1)
        self.assertEqual(graph.get_total_edges(), 0)
        self.assertEqual(len(graph.get_neighbors('milk')), 0)

    def test_empty_transactions(self):
        """Test building graph from empty transaction list"""
        graph = build_graph_from_transactions([])

        self.assertEqual(graph.get_total_items(), 0)

    def test_single_item_basket(self):
        """Test basket with only one item (no pairs possible)"""
        transactions = [
            {'Member_number': '1', 'Date': '01-01-2015', 'itemDescription': 'milk'}
        ]

        graph = build_graph_from_transactions(transactions)

        # Should have 1 item but 0 edges
        self.assertEqual(graph.get_total_items(), 1)
        self.assertEqual(graph.get_total_edges(), 0)


# Run the tests
if __name__ == '__main__':
    print("Running tests for Supermarket Market Basket Analysis...")
    print("="*60)
    unittest.main(verbosity=2)
