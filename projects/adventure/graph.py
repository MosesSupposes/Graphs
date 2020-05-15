"""
Simple graph implementation
"""
from util import Stack, Queue  # These may come in handy
from functools import reduce

class MazeGraph:
    opposite_direction = {"n": "s", "e": "w", "s": "n", "w": "e"}

    """Represent a graph as a dictionary of vertices mapping labels to edges."""
    def __init__(self):
        self.vertices = {}

    def add_vertex(self, vertex_id):
        """
        Add a vertex to the graph.
        """
        if vertex_id not in self.vertices:
            self.vertices[vertex_id] = {}
            return self.vertices[vertex_id]
        else:
            return None

    def add_edge(self, direction, v1, v2):
        """
        Add a directed edge to the graph.
        """
        if v1 in self.vertices:
            self.vertices[v1][direction] = v2
        else:
            self.vertices[v1] = {}
            self.vertices[v1][direction] = v2

    def get_neighbors(self, vertex_id):
        """
        Get all neighbors (edges) of a vertex.
        """
        if vertex_id in self.vertices:
            return self.vertices[vertex_id]
        else:
            return {} 

    def bft(self, starting_vertex):
        """
        Print each vertex in breadth-first order
        beginning from starting_vertex.
        """
        q = Queue()
        q.enqueue(starting_vertex)
        visited = set() 

        while q.size() > 0:
            vertex = q.dequeue()
            print(vertex)
            visited.add(vertex)

            for next_vert in self.get_neighbors(vertex).values():
                if next_vert not in visited:
                    q.enqueue(next_vert)
                    # It hasn't been visited yet, but it will be in the near future.
                    visited.add(next_vert)

    # def dft(self, starting_vertex, cb=print):
    #     """
    #     Print each vertex in depth-first order
    #     beginning from starting_vertex.
    #     """
    #     s = Stack()
    #     s.push(starting_vertex)
    #     visited = set()

    #     while s.size() > 0:
    #         vertex = s.pop()
    #         # if vertex not in visited:
    #         cb(vertex)
    #         visited.add(vertex)

    #         for next_vert in self.get_neighbors(vertex).values():
    #             if next_vert not in visited:
    #                 s.push(next_vert)
    #                 visited.add(next_vert)

    #* An optimization to be made is to not travel to a room that's popped off the stack if that 
    #* room is a dead end.
    def dft(self, player, path_traveled):
        """
        Print each vertex in depth-first order
        beginning from starting_vertex.
        """
        s = Stack()
        s.push(player.current_room)

        while s.size() > 0:
            room = s.pop()

            # If room is in graph and its a dead end, perform a bfs to get unstuck.
            # Once we're unstuck, we can explore the new paths  
            if room.id in self.vertices and self.is_dead_end(room.id):
                # travel to the room we popped off the stack before traversing it.
                directions_to_next_room = self.bfs(player.current_room.id, room.id)
                for direction in directions_to_next_room:
                    player.travel(direction)
                    path_traveled.append(direction)

                shortest_path_to_non_dead_end = self.escape_dead_end_bfs(room.id)
                for direction in shortest_path_to_non_dead_end:
                    player.travel(direction)
                    path_traveled.append(direction)
                for direction in self.vertices[player.current_room.id]:
                    if room == "?":
                        player.travel(direction)
                        path_traveled.append(direction)
                        self.traverse(player, s, path_traveled, player.current_room)

            # If room is in graph and it has unexplored paths, explore those paths
            elif room.id in self.vertices and not self.is_dead_end(room.id):
                # travel to the room we popped off the stack before traversing it
                directions_to_next_room = self.bfs(player.current_room.id, room.id)
                for direction in directions_to_next_room:
                    player.travel(direction)
                    path_traveled.append(direction)

                # explore the room
                for direction in self.vertices[room.id]:
                    if self.vertices[room.id][direction] == "?":
                        player.travel(direction)
                        path_traveled.append(direction)
                        self.traverse(player, s, path_traveled, player.current_room)

            # If the room isn't a vertex in the graph...
            else:
                # add it to the graph and explore it
                self.add_vertex(room.id)
                self.traverse(player, s, path_traveled, room)

        return path_traveled

    def dft_recursive(self, starting_vertex):
        """
        Print each vertex in depth-first order
        beginning from starting_vertex.

        This should be done using recursion.
        """
        def traverse(vertex, visited):
            neighbors = self.get_neighbors(vertex).values()
            if vertex not in visited:
                print(vertex)
                visited.append(vertex)
            
                for next_vert in neighbors:
                    traverse(next_vert, visited)

        return traverse(starting_vertex, [])
                 

    # def bfs(self, starting_vertex, destination_vertex):
    #     """
    #     Return a list containing the shortest path from
    #     starting_vertex to destination_vertex in
    #     breath-first order.
    #     """
    #     q = Queue()
    #     q.enqueue([starting_vertex])
    #     visited = set()

    #     while q.size() > 0:
    #         cur_path = q.dequeue()
    #         if cur_path[-1] == destination_vertex:
    #             return cur_path
    #         else:
    #             for vertex in self.get_neighbors(cur_path[-1]).values():
    #                 if vertex not in visited:
    #                     visited.add(vertex)
    #                     q.enqueue(cur_path + [vertex])
    #     return [] 
    def bfs(self, starting_room_id, destination_room_id):
        """
        Return a list containing the shortest path from
        starting_vertex to destination_vertex in
        breath-first order.
        """
        q = Queue()
        q.enqueue([(None, starting_room_id)])
        visited = set()

        while q.size() > 0:
            cur_path = q.dequeue()
            if cur_path[-1][1] == destination_room_id:
                # Return a list of directions to the path
                directions = list(map(lambda path: path[0], cur_path))
                # The first direction that was added to the queue was None
                return list(filter(lambda direction: direction is not None, directions))
            else:
                for direction, room_id in self.get_neighbors(cur_path[-1][1]).items():
                    if room_id not in visited:
                        visited.add(room_id)
                        q.enqueue(cur_path + [(direction, room_id)])
        return [] 
    def escape_dead_end_bfs(self, starting_room_id):
        """
        Return a list containing the shortest path from
        starting_vertex to destination_vertex in
        breath-first order.
        """
        q = Queue()
        q.enqueue([(None, starting_room_id)])
        visited = set()

        while q.size() > 0:
            cur_path = q.dequeue()
            if not self.is_dead_end(cur_path[-1][1]):
                directions_to_non_dead_end =  list(map(lambda path: path[0], cur_path))
                # The initial item on the queue had a direction of None
                return list(filter(lambda direction: direction is not None, directions_to_non_dead_end))
            else:
                for direction, room_id in self.vertices[cur_path[-1][1]].items():
                    if room_id not in visited:
                        visited.add(room_id)
                        q.enqueue(cur_path + [(direction, room_id)])
        return [] 

    def dfs(self, starting_vertex, destination_vertex):
        """
        Return a list containing a path from
        starting_vertex to destination_vertex in
        depth-first order.
        """
        s = Stack()
        s.push([starting_vertex])
        visited = set()

        while s.size() > 0:
            cur_path = s.pop()
            if cur_path[-1] == destination_vertex:
                return cur_path
            else:
                for vertex in self.get_neighbors(cur_path[-1]).values():
                    if vertex not in visited:
                        visited.add(vertex)
                        s.push(cur_path + [vertex])


    def dfs_recursive(self, starting_vertex, destination_vertex):
        """
        Return a list containing a path from
        starting_vertex to destination_vertex in
        depth-first order.

        This should be done using recursion.
        """
        def find_shortest_path(path, visited):
            if path[-1] == destination_vertex:
                return path
            else:
                visited.append(path[-1])
                for vertex in self.get_neighbors(path[-1]).values():
                    if vertex not in visited:
                        shortest_path = find_shortest_path(path + [vertex], visited)
                        if shortest_path is not None:
                            return shortest_path
                return None       

        return find_shortest_path([starting_vertex], [])
    
    # Traverse an explored room, creating directed links between the room and its neighbors, and populatin 
    # the neigbors' neigbors rooms with "?"s. Also, adding the neigbors' neigbors to the stack for future exploration.
    def traverse(self, player, stack, path_traveled, room):
        for direction in room.get_exits():
            if room.id not in self.vertices:
                player.travel(direction)
                path_traveled.append(direction)
                # Add a directed edge
                self.add_edge(direction, room.id, player.current_room.id)
                self.add_edge(self.opposite_direction[direction], player.current_room.id, room.id)
                # Auto fill the room's exits with a "?" (except for the directed edge from above)
                for direction2 in player.current_room.get_exits():
                    if direction2 != self.opposite_direction[direction]: 
                        if player.current_room.id not in self.vertices or self.vertices[player.current_room.id].get(direction2) is None:
                            self.add_edge(direction2, player.current_room.id, "?")
                # Add this unexplored room to the stack to be traversed later
                if not self.is_dead_end(player.current_room.id):
                    stack.push(player.current_room)
                # Travel back to the starting point 
                player.travel(self.opposite_direction[direction])
                path_traveled.append(self.opposite_direction[direction]) 
            elif (direction not in self.vertices[room.id]) or (direction in self.vertices[room.id] and self.vertices[room.id][direction] == "?"):
                player.travel(direction)
                path_traveled.append(direction)
                # Add a directed edge
                self.add_edge(direction, room.id, player.current_room.id)
                self.add_edge(self.opposite_direction[direction], player.current_room.id, room.id)
                # Auto fill the room's exits with a "?" (except for the directed edge from above)
                for direction2 in player.current_room.get_exits():
                    if direction2 != self.opposite_direction[direction]: 
                        if player.current_room.id not in self.vertices or self.vertices[player.current_room.id].get(direction2) is None:
                            self.add_edge(direction2, player.current_room.id, "?")
                # Add this unexplored room to the stack to be traversed later
                if not self.is_dead_end(player.current_room.id):
                    stack.push(player.current_room)
                # Travel back to the starting point 
                player.travel(self.opposite_direction[direction])
                path_traveled.append(self.opposite_direction[direction])
        
    def is_dead_end(self, room_id):
        if room_id in self.vertices:
            for room in self.vertices[room_id].values():
                if room == "?":
                    return False
            return True
        else:
            raise IndexError("The room with the id of " + room_id + " is not a vertex in the graph.")
        


if __name__ == '__main__':
    graph = MazeGraph()  # Instantiate your graph
    # https://github.com/LambdaSchool/Graphs/blob/master/objectives/breadth-first-search/img/bfs-visit-order.png
    graph.add_vertex(1)
    graph.add_vertex(2)
    graph.add_vertex(3)
    graph.add_vertex(4)
    graph.add_vertex(5)
    graph.add_vertex(6)
    graph.add_vertex(7)
    graph.add_edge("n", 5, 3)
    graph.add_edge("s", 6, 3)
    graph.add_edge("e", 7, 1)
    graph.add_edge("w", 4, 7)
    graph.add_edge("e", 1, 2)
    graph.add_edge("e", 7, 6)
    graph.add_edge("w", 2, 4)
    graph.add_edge("s", 3, 5)
    graph.add_edge("n", 2, 3)
    graph.add_edge("n", 4, 6)

    '''
    Should print:
        {1: {2}, 2: {3, 4}, 3: {5}, 4: {6, 7}, 5: {3}, 6: {3}, 7: {1, 6}}
    '''
    # print(graph.vertices)

    '''
    Valid BFT paths:
        1, 2, 3, 4, 5, 6, 7
        1, 2, 3, 4, 5, 7, 6
        1, 2, 3, 4, 6, 7, 5
        1, 2, 3, 4, 6, 5, 7
        1, 2, 3, 4, 7, 6, 5
        1, 2, 3, 4, 7, 5, 6
        1, 2, 4, 3, 5, 6, 7
        1, 2, 4, 3, 5, 7, 6
        1, 2, 4, 3, 6, 7, 5
        1, 2, 4, 3, 6, 5, 7
        1, 2, 4, 3, 7, 6, 5
        1, 2, 4, 3, 7, 5, 6
    '''
    # graph.bft(1)

    '''
    Valid DFT paths:
        1, 2, 3, 5, 4, 6, 7
        1, 2, 3, 5, 4, 7, 6
        1, 2, 4, 7, 6, 3, 5
        1, 2, 4, 6, 3, 5, 7
    '''
    # graph.dft(1)
    # graph.dft_recursive(1)

    '''
    Valid BFS path:
        [1, 2, 4, 6]
    '''
    print(graph.bfs(1, 6))

    '''
    Valid DFS paths:
        [1, 2, 4, 6]
        [1, 2, 4, 7, 6]
    '''
    # print(graph.dfs(1, 6))
    # print(graph.dfs_recursive(1, 6))
