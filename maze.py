import streamlit as st
from PIL import Image, ImageDraw
import io

# Your existing Node and StackFrontier classes remain unchanged
class Node:
    def __init__(self, state, parent, action):
        self.state = state
        self.parent = parent
        self.action = action

class StackFrontier:
    def __init__(self):
        self.frontier = []
    
    def add(self, node):
        self.frontier.append(node)
    
    def contains_state(self, state):
        return any(node.state == state for node in self.frontier)
    
    def empty(self):
        return len(self.frontier) == 0
    
    def remove(self):
        if self.empty():
            raise Exception("empty frontier")
        else:
            node = self.frontier[-1]
            self.frontier = self.frontier[:-1]
            return node

class Maze:
    # Your existing Maze class remains largely unchanged
    # Only showing modified output_image for better visuals
    def __init__(self, contents):
        # ... (your existing __init__ code) ...
        if contents.count("A") != 1:
            raise Exception("maze must have exactly one start point")
        if contents.count("B") != 1:
            raise Exception("maze must have exactly one goal")

        contents = contents.splitlines()
        self.height = len(contents)
        self.width = max(len(line) for line in contents)

        self.walls = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                try:
                    if contents[i][j] == "A":
                        self.start = (i, j)
                        row.append(False)
                    elif contents[i][j] == "B":
                        self.goal = (i, j)
                        row.append(False)
                    elif contents[i][j] == " ":
                        row.append(False)
                    else:
                        row.append(True)
                except IndexError:
                    row.append(False)
            self.walls.append(row)
        self.solution = None

    def print(self):
        # ... (your existing print code) ...
        solution = self.solution[1] if self.solution is not None else None
        output = []
        for i, row in enumerate(self.walls):
            line = ""
            for j, col in enumerate(row):
                if col:
                    line += "█"
                elif (i, j) == self.start:
                    line += "A"
                elif (i, j) == self.goal:
                    line += "B"
                elif solution is not None and (i, j) in solution:
                    line += "*"
                else:
                    line += " "
            output.append(line)
        return "\n".join(output)

    def output_image(self):
        cell_size = 50
        cell_border = 2
        img = Image.new(
            "RGBA",
            (self.width * cell_size, self.height * cell_size),
            "white"  # Changed to white background
        )
        draw = ImageDraw.Draw(img)

        solution = self.solution[1] if self.solution is not None else None
        for i, row in enumerate(self.walls):
            for j, col in enumerate(row):
                if col:
                    fill = "#2D3748"  # Dark gray walls
                elif (i, j) == self.start:
                    fill = "#EF4444"  # Red start
                elif (i, j) == self.goal:
                    fill = "#10B981"  # Green goal
                elif solution is not None and (i, j) in solution:
                    fill = "#FBBF24"  # Yellow path
                elif (i, j) in self.explored:
                    fill = "#60A5FA"  # Blue explored
                else:
                    fill = "#FFFFFF"  # White empty

                draw.rectangle(
                    ([(j * cell_size + cell_border, i * cell_size + cell_border),
                      ((j + 1) * cell_size - cell_border, (i + 1) * cell_size - cell_border)]),
                    fill=fill,
                    outline="#E5E7EB"  # Light gray borders
                )
        return img

    # ... (your existing neighbors and solve methods remain unchanged) ...
    def neighbors(self, state):
        row, col = state
        candidates = [
            ("up", (row - 1, col)),
            ("down", (row + 1, col)),
            ("left", (row, col - 1)),
            ("right", (row, col + 1))
        ]

        result = []
        for action, (r, c) in candidates:
            if 0 <= r < self.height and 0 <= c < self.width and not self.walls[r][c]:
                result.append((action, (r, c)))
        return result

    def solve(self):
        self.num_explored = 0
        start = Node(state=self.start, parent=None, action=None)
        frontier = StackFrontier()
        frontier.add(start)
        self.explored = set()

        while True:
            if frontier.empty():
                raise Exception("no solution")

            node = frontier.remove()
            self.num_explored += 1

            if node.state == self.goal:
                actions = []
                cells = []
                while node.parent is not None:
                    actions.append(node.action)
                    cells.append(node.state)
                    node = node.parent
                actions.reverse()
                cells.reverse()
                self.solution = (actions, cells)
                return

            self.explored.add(node.state)

            for action, state in self.neighbors(node.state):
                if not frontier.contains_state(state) and state not in self.explored:
                    child = Node(state=state, parent=node, action=action)
                    frontier.add(child)

# Enhanced Streamlit app
def main():
    # Custom CSS for professional look
    st.markdown("""
        <style>
        .main {
            background-color: #F9FAFB;
            padding: 2rem;
        }
        .stButton>button {
            background-color: #3B82F6;
            color: white;
            border-radius: 8px;
            padding: 0.5rem 1rem;
        }
        .stButton>button:hover {
            background-color: #2563EB;
        }
        .card {
            background-color: white;
            padding: 1.5rem;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 1rem;
        }
        h1 {
            color: #1F2937;
            font-weight: 700;
        }
        h2 {
            color: #4B5563;
            font-weight: 600;
        }
        </style>
    """, unsafe_allow_html=True)

    # Header
    st.title("Maze Solver")
    st.markdown("A professional maze solving tool with visual output")

    # Layout with columns
    col1, col2 = st.columns([1, 1])

    with col1:
        # Input section
        with st.container():
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.subheader("Upload Your Maze")
            st.markdown("Upload a .txt file using 'A' for start, 'B' for goal, '#' for walls, and spaces for paths.")
            
            uploaded_file = st.file_uploader(
                "Choose a maze file",
                type="txt",
                help="Upload a text file containing your maze"
            )
            st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        # Example section
        with st.container():
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.subheader("Maze Format Example")
            example = "#####\n#A  #\n# # #\n#  B#\n#####"
            st.code(example, language="text")
            st.markdown('</div>', unsafe_allow_html=True)

    # Processing and results
    if uploaded_file is not None:
        try:
            contents = uploaded_file.read().decode("utf-8")
            maze = Maze(contents)

            # Results section
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.subheader("Maze Solution")
            
            col_maze, col_stats = st.columns([3, 1])
            
            with col_maze:
                with st.spinner("Solving maze..."):
                    maze.solve()
                img = maze.output_image()
                st.image(
                    img,
                    caption="Solution Visualization\nRed: Start | Green: Goal | Yellow: Path | Blue: Explored",
                    use_column_width=True
                )
            
            with col_stats:
                st.metric("States Explored", maze.num_explored)
                st.text_area(
                    "Text Solution",
                    maze.print(),
                    height=150
                )
            
            st.markdown('</div>', unsafe_allow_html=True)

        except Exception as e:
            st.error(f"Error: {str(e)}", icon="🚨")

if __name__ == "__main__":
    main()