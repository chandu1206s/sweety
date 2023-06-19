import hashlib
import matplotlib.pyplot as plt
import networkx as nx
from queue import PriorityQueue


class MerkleTree:
    def __init__(self, data):
        self.data = data
        self.tree = self.build_tree(self.data)

    def build_tree(self, data):
        tree = []
        for item in data:
            tree.append(self.hash(item))
        i = len(data)
        while i > 1:
            temp = []
            for j in range(0, i, 2):
                if j + 1 < i:
                    temp.append(self.hash(tree[j] + tree[j + 1]))
                else:
                    temp.append(tree[j])
            tree = temp
            i = len(tree)
        return tree[0]

    def hash(self, item):
        return hashlib.sha256(item.encode('utf-8')).hexdigest()


class CloudResource:
    def __init__(self, name, priority, allocated=False):
        self.name = name
        self.priority = priority
        self.allocated = allocated

    def __lt__(self, other):
        return self.priority < other.priority


class CloudResourceAllocator:
    def __init__(self):
        self.resources = PriorityQueue()
        self.merkle_tree = None
        self.graph = nx.Graph()

    def allocate_resource(self, resource):
        if not resource.allocated:
            self.resources.put(resource)
            resource.allocated = True

    def deallocate_resource(self, resource_name):
        deallocated_resource = None
        resources_copy = []
        while not self.resources.empty():
            resource = self.resources.get()
            if resource.name == resource_name:
                deallocated_resource = resource
            else:
                resources_copy.append(resource)
        for resource in resources_copy:
            self.resources.put(resource)
        if deallocated_resource:
            deallocated_resource.allocated = False
        return deallocated_resource

    def build_merkle_tree(self):
        resource_names = [resource.name for resource in self.resources.queue]
        self.merkle_tree = MerkleTree(resource_names)

    def verify_merkle_tree(self):
        if not self.merkle_tree:
            print("Merkle tree not built.")
            return False
        resource_names = [resource.name for resource in self.resources.queue]
        return self.merkle_tree.tree == self.merkle_tree.build_tree(resource_names)

    def get_allocated_resources(self):
        return [resource.name for resource in self.resources.queue if resource.allocated]

    def get_resource_by_name(self, resource_name):
        for resource in self.resources.queue:
            if resource.name == resource_name:
                return resource
        return None

    def visualize_resources(self):
        labels = {}
        positions = {}
        colors = []

        for i, resource in enumerate(self.resources.queue):
            labels[i] = resource.name
            positions[i] = (resource.priority, -i)
            colors.append(resource.priority)

        self.graph.clear()
        self.graph.add_nodes_from(range(len(self.resources.queue)))
        self.graph.add_edges_from([(i, i+1) for i in range(len(self.resources.queue)-1)])
        edge_labels = {(i, i+1): '' for i in range(len(self.resources.queue)-1)}

        plt.figure(figsize=(10, 6))
        nx.draw(self.graph, pos=positions, node_color=colors, cmap='coolwarm', node_size=500, with_labels=False)
        nx.draw_networkx_labels(self.graph, pos=positions, labels=labels)
        nx.draw_networkx_edge_labels(self.graph, pos=positions, edge_labels=edge_labels, font_color='gray')

        plt.title("Cloud Resource Allocation")
        plt.xlabel("Priority")
        plt.ylabel("Resource")
        plt.xticks([])
        plt.yticks([])

        plt.show()


def print_menu():
    print("\nResource Allocation System Menu:")
    print("1. Allocate a resource")
    print("2. Deallocate a resource")
    print("3. Build Merkle tree")
    print("4. Verify Merkle tree")
    print("5. Get allocated resources")
    print("6. Search for a resource by name")
    print("7. Visualize resources")
    print("0. Exit")


def get_valid_input(prompt, input_type):
    while True:
        try:
            if input_type == int:
                return int(input(prompt))
            elif input_type == str:
                return input(prompt)
            else:
                raise ValueError()
        except ValueError:
            print("Invalid input. Please try again.")


def main():
    allocator = CloudResourceAllocator()

    while True:
        print_menu()
        choice = get_valid_input("Enter your choice: ", int)

        if choice == 1:
            name = get_valid_input("Enter the name of the resource: ", str)
            priority = get_valid_input("Enter the priority of the resource: ", int)
            resource = CloudResource(name, priority)
            allocator.allocate_resource(resource)
            print("Resource allocated successfully.")

        elif choice == 2:
            name = get_valid_input("Enter the name of the resource to deallocate: ", str)
            deallocated_resource = allocator.deallocate_resource(name)
            if deallocated_resource:
                print("Resource deallocated successfully.")
            else:
                print("Resource not found.")

        elif choice == 3:
            allocator.build_merkle_tree()
            print("Merkle tree built successfully.")

        elif choice == 4:
            if allocator.verify_merkle_tree():
                print("Merkle tree verified successfully.")
            else:
                print("Merkle tree verification failed.")

        elif choice == 5:
            allocated_resources = allocator.get_allocated_resources()
            print("Allocated resources:", allocated_resources)

        elif choice == 6:
            name = get_valid_input("Enter the name of the resource to search: ", str)
            resource = allocator.get_resource_by_name(name)
            if resource:
                print("Resource found: ", resource.name, "with priority:", resource.priority)
            else:
                print("Resource not found.")

        elif choice == 7:
            allocator.visualize_resources()

        elif choice == 0:
            print("Exiting...")
            break

        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()
