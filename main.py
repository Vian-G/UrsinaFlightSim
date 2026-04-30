from ursina import *

from re import search
from matplotlib import pyplot
from pathlib import Path
from datetime import datetime, timezone
import csv
import json
import shutil
from matrix import Matrix
from user_management import User, UserManager
from plane_management import PlaneManager


#############################################################
################# GLOBAL VARIABLES/STATE ####################
#############################################################
                
current_user = None    # will store the logged-in user
flight_time = 0        # total flight time in seconds
crashed = False        # indicates if the plane crashed

#############################################################
##################### URSINA SCREENS ########################
#############################################################

# Initialize the Ursina game engine with configuration settings

'''Ursina(title='ursina', icon='textures/ursina.ico', borderless:bool=None, fullscreen:bool=None, size=None,
    forced_aspect_ratio=None, position=None, vsync=True, editor_ui_enabled:bool=None, window_type='onscreen',
    development_mode:bool=None, render_mode=None, show_ursina_splash=False, use_ingame_console=False)
'''
app = Ursina(title = 'Flight Sim',
             development_mode = False,
             icon='icon.ico',
             borderless = False,
             size = [1920,1080],
             forced_aspect_ratio = True)
Text.default_origin = (0, 0)
Text.default_font = "VeraMono.ttf"

# ---------------------------
#    LOGIN SCREEN   
# ---------------------------
class LoginScreen(Entity):
    """
    Login screen UI implementation.
    Demonstrates UI design and event handling in Ursina.
    """
    def __init__(self, user_manager):
        super().__init__()
        self.user_manager = user_manager
        # Create UI elements with precise positioning
        self.title = Text(text = 'Flight Simulator', position = (0, 0.3), origin = (0, 0), scale = (3, 3))
        self.username_txt = Text(text = 'Username:', position = (-0.25, 0.1), origin = (0, 0), scale = (1.3, 1.3))
        self.password_txt = Text(text = 'Password:', position = (-0.25, 0), origin = (0, 0), scale = (1.3, 1.3))
        self.username_field = InputField(position = (0, 0.1), scale = (0.3, 0.05))
        self.password_field = InputField(position = (0, 0), scale = (0.3, 0.05), hide_content = True)
        self.login_button = Button(text = 'Login', position = (0, -0.1), scale = (0.2, 0.05))
        self.register_button = Button(text = 'Register', position = (0, -0.2), scale = (0.2, 0.05))

        # Set up event handlers
        self.login_button.on_click = self.attempt_login
        self.register_button.on_click = self.go_to_register

        self.info_text = Text(text = '', position = (0, -0.3), origin = (0, 0), scale = 1.5)

    def attempt_login(self):
        """
        Validates user credentials and handles login attempt.
        Uses the UserManager for authentication.
        """
        username = self.username_field.text
        password = self.password_field.text
        user = self.user_manager.login(username, password)
        if user:
            global current_user
            current_user = user
            self.info_text.text = 'Login successful!'
            self.info_text.origin = (0, 0)
            self.start_main_menu()
        else:
            self.info_text.text = 'Login failed. Please try again.'
            self.info_text.origin = (0, 0)

    def clear_page(self):
        """
        Cleans up UI elements when transitioning to another screen.
        Demonstrates proper resource management.
        """
        # destroy each UI element
        destroy(self.title)
        destroy(self.username_field)
        destroy(self.password_field)
        destroy(self.username_txt)
        destroy(self.password_txt)
        destroy(self.login_button)
        destroy(self.register_button)
        destroy(self.info_text)

    def go_to_register(self):
        """
        Transitions to the registration screen.
        """
        self.clear_page()
        
        # Transition to Register Screen
        RegisterScreen(self.user_manager)  

    def start_main_menu(self):
        """
        Transitions to the main menu screen after successful login.
        """
        self.clear_page()
                
        # Transition to the main menu
        MainMenu()

# ---------------------------
#       REGISTER SCREEN   
# ---------------------------
class RegisterScreen(Entity):
    """
    Registration screen UI implementation.
    Demonstrates form validation and password policy enforcement.
    """
    def __init__(self, user_manager):
        super().__init__()
        self.user_manager = user_manager
        self.username_txt = Text(text = 'Username:', position = (-0.25, 0.1), origin = (0, 0), scale = (1.3, 1.3))
        self.password_txt = Text(text = 'Password:', position = (-0.25, 0), origin = (0, 0), scale = (1.3, 1.3))
        
        self.title = Text(text = 'Register', position = (0, 0.3), origin = (0, 0), scale = (3, 3))
        self.username_field = InputField(default_value = '', position = (0, 0.1), scale = (0.3, 0.05))
        self.password_field = InputField(default_value = '', position = (0, 0), scale = (0.3, 0.05), hide_content = True)
        self.register_button = Button(text = 'Register', position = (0, -0.1), scale = (0.2, 0.05))
        self.back_button = Button(text = 'Back to Login', position = (0, -0.2), scale = (0.2, 0.05))

        self.register_button.on_click = self.attempt_register
        self.back_button.on_click = self.back_to_login

        self.info_text = Text(text = '', position = (0, -0.3), scale = 1.5)

    def attempt_register(self):
        """
        Validates input and attempts to register a new user.
        Implements password policy checks:
        - Minimum length
        - No repeated characters
        - No repeated patterns
        """
        username = self.username_field.text.strip()
        password = self.password_field.text.strip()

        # Form validation
        if not username or not password:
            self.info_text.text = "Username and password cannot be empty!"
            self.info_text.origin = (0, 0)
            return
        
        if len(password) < 8:
            self.info_text.text = "Password must be atleast 8 characters long!"
            self.info_text.origin = (0, 0)
            return
            
        # Password strength check 1: No three consecutive identical characters
        if search(r'(.)\1{2}', password):
            self.info_text.text = "Password cannot have 3 consecutive identical characters!"
            self.info_text.origin = (0, 0)
            return
            
        # Password strength check 2: No repeating patterns
        if search(r'(..)\1', password):
            self.info_text.text = "Password cannot have consecutive identical character pairs!"
            self.info_text.origin = (0, 0)
            return

        if not (search(r'\d', password) and search(r'[!@#$%^&*(),.?":{}|<>]', password) and search(r'[A-Z]', password)):
            self.info_text.text = "Password must contain at least 1 digit,\n 1 special character, and 1 uppercase letter!"
            self.info_text.origin = (0, 0)
            return
            
        # Attempt registration
        if self.user_manager.register_user(username, password):
            self.info_text.text = "Registration successful! Returning to login..."
            self.info_text.origin = (0, 0)
            invoke(self.back_to_login, delay = 1)  # Auto-return after success
        else:
            self.info_text.text = "Username already exists. Try another one."
            self.info_text.origin = (0, 0)

    def back_to_login(self):
        """
        Returns to the login screen.
        Demonstrates proper UI cleanup.
        """
        destroy(self.title)
        destroy(self.username_field)
        destroy(self.password_field)
        destroy(self.register_button)
        destroy(self.back_button)
        destroy(self.info_text)
        destroy(self.username_txt)
        destroy(self.password_txt)
        LoginScreen(self.user_manager)  # Go back to login screen

# ---------------------------
#       MAIN MENU SCREEN    
# ---------------------------
class MainMenu(Entity):
    """
    Main menu with aircraft selection.
    Demonstrates dynamic UI creation and component interaction.
    """
    def __init__(self, plane_manager = PlaneManager()):
        super().__init__()
        camera.orthographic = True
        camera.fov = 1
        
        # Get planes from plane manager
        self.plane_manager = plane_manager
        self.planes = self.plane_manager.get_all_planes_info()
        
        # Set up UI
        self.title = Text(text = 'Flight Simulator Main Menu', position = (0, 0.4), origin = (0, 0), scale = (2, 2))
        
        # Display user level
        global current_user
        self.user_level_text = Text(
            text = f'Pilot Level:\n{current_user.level} / 10',
            position = (-0.66, 0.4),
            origin = (0, 0),
            scale = (1.3, 1.3),
            color = color.yellow)
            
        self.flight_time_text = Text(
            text = f'Total Flight Time:\n{current_user.flight_minutes:.2f} mins',
            position = (0.66, 0.4),
            origin = (0, 0),
            scale = (1.3, 1.3),
            color = color.yellow)
            
        # Add level system explanation
        self.level_info = Text(
            text =
            '''Complete flights successfully to level up.\nCrashes will decrease your level.\nHigher levels unlock better aircraft!''',
            position = (0, 0.3),
            origin = (0, 0),
            scale = (1, 1),
            color = color.white)
        
        self.start_button = Button(text = 'Start Flight Simulation', position = (0, -0.35), scale = (0.45, 0.05))
        self.start_button.on_click = self.start_simulation
        self.quit_button = Button(text = 'Quit', position = (0, -0.45), scale = (0.25, 0.05))
        self.quit_button.on_click = application.quit

        # Dictionary mapping plane names to handler functions
        self.button_dict = {}
        for plane in self.planes:
            self.button_dict[plane[1]] = self.set_plane
    
        self.buttons = {}  # Store button references for updating color
        self.descriptions = []
        self.images = []
        self.selected_plane = None  # Track selected aircraft
        self.locked_text = []  # Track locked plane text indicators

        # Create buttons in a horizontal layout
        position_x = -0.66      # Initial X position
        offset = position_x/-2  # Spacing between buttons


        # Create thumbnail images and descriptions
        for i in range(len(self.planes)):
            plane = self.planes[i]
            plane_level = plane[0]  # Level requirement for the plane
            plane_name = plane[1]   # Name of the plane
            self.display_plane(plane[2], plane[3], offset * i + position_x, plane_level)

        # Create plane selection buttons
        for i, plane in enumerate(self.planes):
            plane_name = plane[1]
            plane_level = plane[0]
            
            # Create the button
            button = Button(
                text = plane_name,
                scale = (0.25, 0.05),
                position = (position_x, -0.25),
                color = color.black90 if plane_level <= current_user.level else color.gray.tint(-0.4))
                
            # Set button behavior based on level requirement
            if plane_level <= current_user.level:
                button.on_click = Func(self.set_plane, plane_name)  # Enable selection
            else:
                button.disabled = True  # Disable the button
                
            self.buttons[plane_name] = button  # Store reference
            position_x += offset

        # Set default selection to the highest level plane available to the user
        available_planes = [p[1] for p in self.planes if p[0] <= current_user.level]
        if available_planes:
            self.set_plane(available_planes[-1])
        else:
            # Fallback to the first plane if somehow no planes are available
            self.set_plane(self.planes[0][1])

    def display_plane(self, image_path, description_path, x, level_req):
        """
        Displays a plane thumbnail and description.
        Demonstrates file I/O for loading descriptions and images.
        """
        # Show plane thumbnail
        self.images.append(Entity(model = 'quad', texture = image_path, position = (x, 0.12), scale = (0.25, 0.2), z = 2))
        
        # Read description from file
        f = open(description_path, "r")
        desc_text = f.read()
        f.close()
        
        # Add description text
        self.descriptions.append(Text(text = desc_text, position = (x-0.128, 0.01), wordwrap = 10, scale = 0.8))
        
        # Add "LOCKED" overlay for planes that require higher level
        if level_req > current_user.level:
            locked = Text(
                text = f"LOCKED\nRequires\nLevel {level_req}",
                position = (x, 0.12),
                origin = (0, 0),
                scale = (1, 1),
                color = color.red,
                background = True,
                background_color = color.black50,
                z = 3)
            self.locked_text.append(locked)
            

    def set_plane(self, plane_name):
        """
        Selects a plane and updates the UI.
        Demonstrates visual feedback in UI.
        """
        # Reset all buttons to default color
        for btn in self.buttons.values():
            if not btn.disabled:
                btn.color = color.black90

        # Highlight the selected button
        self.buttons[plane_name].color = color.gray
        self.selected_plane = plane_name
       
    def start_simulation(self):
        """
        Cleans up UI and transitions to the flight simulator.
        """
        for btn in self.buttons.values():
            destroy(btn)
        for img in self.images:
            destroy(img)
        for txt in self.descriptions:
            destroy(txt)
        for locked in self.locked_text:
            destroy(locked)
        
        destroy(self.title)
        destroy(self.user_level_text)
        destroy(self.flight_time_text)
        destroy(self.level_info)
        destroy(self.start_button)
        destroy(self.quit_button)
        FlightSimulator(self.selected_plane, self.plane_manager)

# ---------------------------
#       FLIGHT SIMULATOR
# ---------------------------
class FlightSimulator(Entity):
    """
    Core flight simulator implementation.
    Demonstrates advanced physics simulation using:
    - State-space model for aircraft dynamics
    - Matrix operations for state updates
    - 3D transformations for aircraft motion
    - Real-time control input handling
    """
    def __init__(self, selected_plane, plane_manager):
        super().__init__()
        self.plane_manager = plane_manager
        self.plane_physics = self.plane_manager.get_plane_physics(selected_plane)

        self.setup_physics()
        
        # Configure 3D environment
        self.sky = Sky(texture = 'sky_sunset')
        self.setup_ground()
          
        camera.orthographic = False
        camera.fov = 90

        # State vectors for aircraft dynamics:
        # Longitudinal: [velocity, angle_of_attack, pitch_angle, pitch_rate]
        # Lateral: [sideslip_angle, roll_rate, yaw_angle, roll_angle]
        self.state_long = Matrix([[0], [0], [0], [0]])
        self.state_lat = Matrix([[0], [0], [0], [0]])

        self.dt = 0.01667       # Time step (~60 FPS)
        self.flight_time = 0    # Local flight timer
        self.run = True
        self.menu_active = False  # Track if escape menu is open
        self.crashed = False      # Track if aircraft has crashed

        # Ground collision parameters
        self.ground_y = -100      # Ground altitude (matching setup_ground)
        self.crash_message = None # Placeholder for crash message

        # Control surface deflections
        self.elevator = 0  # Pitch control
        self.aileron = 0   # Roll control
        self.rudder = 0    # Yaw control

        # UI elements
        self.setup_overlay()
        self.setup_esc_menu()

        # Data collection lists for graphs
        self.time_data = []
        self.aoa_data = []       # Angle of Attack (state_long[1])
        self.velocity_data = []  # Velocity (state_long[0] + cruise_speed)
        self.gforce_data = []    # G-Force (approximated from vertical acceleration)
        self.altitude_data = []  # Altitude (plane.y - ground_y)

    def setup_ground(self):
        """
        Creates a large textured ground plane below the aircraft.
        Provides visual reference for altitude and motion.
        """
        # Create a large plane for the ground
        self.ground_size = 50000  # Size of the ground plane
        self.ground_y = -100 # Ground altitude
        
        # Create ground mesh
        self.ground = Entity(
            model = 'plane',
            scale = (self.ground_size, 1, self.ground_size),
            position = (0, self.ground_y, 0),
            collider = None,  # No need for physical collider, we'll handle collision manually
            texture = 'white_cube',  # Use a default texture
            texture_scale = (self.ground_size/20, self.ground_size/20),  # Repeat texture to avoid stretching
            color = color.green.tint(-0.3))  # Adjust color to look like terrain

    def check_ground_collision(self):
        """
        Checks if the aircraft has collided with the ground.
        Ends the flight if a collision is detected.
        """
        # Get the lowest point of the aircraft (assuming the plane's pivot is at its center)
        # Add a small buffer (e.g., 1 unit) to account for the size of the aircraft model
        aircraft_lowest_point = self.plane.y - 1
        
        # Check if the aircraft's lowest point is at or below ground level
        if aircraft_lowest_point <= self.ground_y:
            self.crashed = True
            self.run = False
            
            # Create crash message
            self.crash_message = Text(
                text = 'AIRCRAFT CRASHED!',
                position = (0, 0.2),
                origin = (0, 0),
                scale = 3,
                color = color.red)
                
            # Add "Continue" button to proceed to post-flight analysis
            self.continue_button = Button(
                parent = camera.ui,
                text = 'Continue to Analysis',
                position = (0, 0),
                scale = (0.4, 0.08),
                color = color.gray.tint(.2),
                highlight_color = color.gray.tint(.4),
                on_click = self.end_simulation)
            
            # Optional: Add dramatic visual/audio effects for crash
            # For example, change the plane color to indicate damage
            self.plane.color = color.red

    def setup_physics(self):
        """
        Sets up aircraft model and loads physics matrices.
        Demonstrates file I/O for loading simulation parameters.
        State-space model matrices A, B, C, D represent aircraft dynamics.
        """
        # Load 3D model and texture
        self.plane = Entity(
            model = self.plane_physics[0],
            texture = self.plane_physics[1],
            scale = 1,
            rotation = (0, 0, 0),
            position = (0, -2, 20))

        # Load state-space matrices from file
        matrix_path = self.plane_physics[2]
        f = open(matrix_path, "r")
        full_string = f.read()
        f.close()
        
        # Parse matrix data from file
        matrix_combo = [list(map(float, row.split(','))) for row in full_string.split('\n')]
        
        # Create state-space model matrices
        # A and B matrices for longitudinal dynamics (pitch, velocity)
        self.A = Matrix(matrix_combo[0:4])
        self.B = Matrix(matrix_combo[4:8])
        
        # C and D matrices for lateral dynamics (roll, yaw)
        self.C = Matrix(matrix_combo[8:12])
        self.D = Matrix(matrix_combo[12:16])

    def setup_overlay(self):
        """
        Initialize UI elements for flight information display.
        Demonstrates layered UI design with parent-child relationships.
        """
        # Explicitly create and assign each bar without setattr
        self.elevator_bar_bg, self.elevator_bar_fill = self.create_bar(-0.85, color.green)
        self.aileron_bar_bg, self.aileron_bar_fill = self.create_bar(-0.80, color.blue)
        self.rudder_bar_bg, self.rudder_bar_fill = self.create_bar(-0.75, color.yellow)
        self.vv_bar_bg, self.vv_bar_fill = self.create_bar(0.85, color.red)
        
        # Add altitude display (moved outside loop)
        self.altitude_text = Text(
            text = 'Altitude: 0 m',
            position = (0.6, -0.4),
            origin = (0, 0),
            scale = 1.5)
        
        self.crosswind_button = Button(
          parent = camera.ui,
          text = 'Crosswind: Off',
          position = (0.75, 0.42),
          scale = (0.22,0.05),
          color = color.gray.tint(.1),
          on_click = self.toggle_crosswind)

        self.wind_text = Text(
            parent = camera.ui,
            text = 'Wind: 0 m/s',
            position = (0.75, 0.36),
            origin = (0, 0),
            scale = 1.0)
    def toggle_crosswind(self):
        """
        Crosswind toggle and UI update
        """
        self.crosswind_enabled = not self.crosswind_enabled
        if self.crosswind_enabled:
            ws = self.weather.randomWind()
            self.crosswind_button.text = 'Crosswind: On'
            self.wind_text.text = f'Wind: {ws:.2f} m/s'
        else:
            self.weather.calmWind()
            self.crosswind_button.text = 'Crosswind: Off'
            self.wind_text.text = 'Wind: 0 m/s'

        # Updated instructions text (moved outside loop)
        self.instructions = Text(
            text = 'Controls:\nW/S: Elevator (Pitch)\nQ/E: Aileron (Roll)\nA/D: Rudder (Yaw)\nESC: Menu',
            position = (-0.5, 0.4),
            origin = (0, 0),
            scale = 1.5)

    def create_bar(self, pos, fill_color):
        bg = Entity(parent = camera.ui, model = 'quad', color = color.gray, scale = (0.03, 0.5), position = (pos, 0))
        fill = Entity(parent = bg, model = 'quad', color = fill_color, scale = (0.8, 0), position = (0, 0))
        return bg, fill

    def setup_esc_menu(self):
        """
        Create a pause menu that appears when ESC is pressed.
        The menu allows the player to resume or exit the simulation.
        """
        # Create menu container (initially hidden)
        self.menu_panel = Entity(
            parent = camera.ui,
            model = 'quad',
            color = color.black66,
            scale = (0.4, 0.3),
            position = (0, 0),
            enabled = False)
        
        # Menu title
        self.menu_title = Text(
            parent = self.menu_panel,
            text = 'PAUSED',
            position = (0, 0.1),
            origin = (0, 0),
            scale = 2,
            color = color.white)
        
        # Resume button
        self.resume_button = Button(
            parent = self.menu_panel,
            text = 'Resume Flight',
            position = (0, 0),
            scale = (0.8, 0.1),
            color = color.azure,
            highlight_color = color.azure.tint(.2),
            on_click = self.resume_game)
        
        # Exit button
        self.exit_button = Button(
            parent = self.menu_panel,
            text = 'End Flight',
            position = (0, -0.12),
            scale = (0.8, 0.1),
            color = color.red.tint(.2),
            highlight_color = color.red.tint(.4),
            on_click = self.exit_game)
        
        # Set up input handler for ESC key
        self.input_handler = Entity()
        self.input_handler.input = self.handle_input

    def handle_input(self, key):
        """
        Handle keyboard input for the ESC key to toggle the menu.
        """
        if key ==  'escape':
            self.toggle_menu()

    def toggle_menu(self):
        """
        Toggle the visibility of the pause menu and update the simulation state.
        """
        self.menu_active = not self.menu_active
        self.menu_panel.enabled = self.menu_active
        
        # Pause/resume the simulation
        self.run = not self.menu_active
        
        # Disable/enable mouse control for menu interaction
        mouse.locked = not self.menu_active
        mouse.visible = self.menu_active

    def resume_game(self):
        """
        Resume the game when the resume button is clicked.
        """
        self.menu_active = False
        self.menu_panel.enabled = False
        self.run = True
        mouse.locked = True
        mouse.visible = False

    def exit_game(self):
        """
        Exit the simulation when the exit button is clicked.
        """
        self.run = False
        self.end_simulation()

    def update(self):
        """
        Main update loop for the flight simulator.
        Called every frame by the Ursina engine.
        Implements the simulation time step and physics updates.
        """
        if not self.run:
            if not self.menu_active and not self.crashed:  # If not running and not in menu/crash state
                return

        if self.run:  # Only update simulation if running
            self.flight_time += self.dt

            # Update control inputs based on keyboard
            self.update_control_inputs()

            # Update aircraft state using state-space model
            self.update_state_vectors()

            # Update aircraft position and rotation
            self.update_plane()
            
            # Check for ground collision
            self.check_ground_collision()

            # Update camera position to follow aircraft
            self.update_camera()
            
            # Update UI elements
            self.render_overlay()

            # Update data collection lists for graphs
            self.update_data()

            # End simulation after 120 seconds
            if self.flight_time > 120:
                self.run = False
                self.end_simulation()

    def update_control_inputs(self):
        """
        Update elevator, aileron, and rudder based on user input.
        Demonstrates real-time control input handling.
        """
        self.elevator = self.update_control_surface(self.elevator, 'w', 's', 5)
        self.aileron = self.update_control_surface(self.aileron, 'e', 'q', 5)
        self.rudder = self.update_control_surface(self.rudder, 'a', 'd', 5)

    def update_control_surface(self, control, increase_key, decrease_key, maximum):
        """
        Helper method to update a control surface based on user input.
        Implements proportional control with spring-back behavior.
        """
        # Apply input based on key presses within limits
        if held_keys[increase_key] and control < maximum:
            control += 3 * self.dt
        elif held_keys[decrease_key] and control > -maximum:
            control -=  3 * self.dt
        # Spring-back effect when no keys are pressed
        elif control > 0:
            control -=  5 * self.dt
        elif control < 0:
            control += 5 * self.dt
        # Snap to zero for very small values
        if abs(control) < 10 * self.dt and not (held_keys[increase_key] or held_keys[decrease_key]):
            control = 0
        return control

    def update_state_vectors(self):
        """
        Updates longitudinal and lateral state vectors using state-space model.
        
        This implements a discrete-time linear state-space model:
        x[k+1] = x[k] + (Ax[k] + Bu[k])*dt
        
        Where:
        - A, B, C, D are the state-space matrices representing aircraft dynamics
        - x is the state vector (position, velocity, angles, rates)
        - u is the control input vector (elevator, aileron, rudder)
        - dt is the time step
        
        Demonstrates advanced aerospace concepts:
        - State-space representation of dynamic systems
        - Discrete-time integration using Euler method
        - Aircraft stability and control theory
        """
        # Update longitudinal state using matrix operations
        # State vector: [velocity, angle_of_attack, pitch_angle, pitch_rate]
        # Control input: elevator deflection (affects pitch primarily)
        self.state_long += (self.A * self.state_long + self.B * self.elevator) * self.dt
        
        # Update lateral state using matrix operations
        # State vector: [sideslip_angle, roll_rate, yaw_angle, roll_angle]
        # Control inputs: aileron (roll) and rudder (yaw) deflections, constructed in to an input matrix
        self.state_lat += (self.C * self.state_lat + self.D * Matrix([[self.aileron], [self.rudder]])) * self.dt

    def update_plane(self):
        """
        Updates plane position and rotation based on state vectors.
        
        Demonstrates advanced aerodynamics and flight physics:
        - Coordinate system transformations between body and earth frames
        - Six degrees of freedom (6DOF) aircraft movement
        - Euler angle rotations and their applications
        - Velocity decomposition into forward, vertical, and horizontal components
        
        Uses the custom Matrix class for all calculations, showing practical
        application of the OOP principles implemented earlier.
        """
        # Scale factor to convert physical units to visual representation
        movment_scale = 1e-3
        
        # Extract state variables and convert from degrees to radians where needed
        # 57.2958 is the conversion factor (180/π)
        sidelip_angle = self.state_lat.getmatrix()[0][0] / 57.2958  # Sideslip angle in radians
        pitch_angle = -self.state_long.getmatrix()[2][0] / 57.2958  # Pitch angle in radians (note: negated)
        yaw_angle = self.state_lat.getmatrix()[2][0] / 57.2958      # Yaw angle in radians
        roll_angle = self.state_lat.getmatrix()[3][0] / 57.2958     # Roll angle in radians
        
        # Calculate velocity components
        # Adds cruise speed to current velocity perturbation (state-space models work with perturbations)
        cruise_speed = self.A.getmatrix()[1][2] / movment_scale # Extract cruise speed from A matrix (encapsulation)
        v = self.state_long.getmatrix()[0][0] + cruise_speed # Total airspeed
        
        # Decompose velocity into components using trigonometric relationships
        fv = v * cos(sidelip_angle)  # Forward velocity component
        vv = self.state_long.getmatrix()[1][0]  # Vertical velocity component (from angle of attack)
        hv = v * sin(sidelip_angle)  # Horizontal (sideways) velocity component
        
        # Update aircraft orientation using Euler angle transformations
        # These equations implement a simplified form of the rotation matrix transformations
        # Combines pitch and yaw effects based on current roll angle
        self.plane.rotation_x += 57.2958 * (pitch_angle * cos(roll_angle) + yaw_angle * sin(roll_angle)) * self.dt
        self.plane.rotation_y += 57.2958 * (pitch_angle * sin(roll_angle) + yaw_angle * cos(roll_angle)) * self.dt
        self.plane.rotation_z = 57.2958 * roll_angle  # Direct mapping for roll angle
        
        # Update aircraft position using velocity components in aircraft body axes
        # Multiply by time step (dt) and scaling factor to get position change
        # Uses Ursina's vector operations through forward, up, and right vectors
        self.plane.position += self.plane.forward * fv * self.dt * movment_scale
        self.plane.position += self.plane.up * vv * self.dt * movment_scale
        self.plane.position += self.plane.right * hv * self.dt * movment_scale

        if self.crosswind_enabled:
            wind_speed = self.weather.wind_x
            self.plane.position += self.plane.right * wind_speed * self.dt * movment_scale
            self.wind_text.text = f'Wind: {wind_speed:.2f} m/s'

        if self.plane.x > (self.ground_size / 4) or self.plane.z > (self.ground_size / 4):
            self.plane.x = 0
            self.plane.z = 0

    def update_camera(self):
        """
        Updates camera position and rotation to follow the aircraft.
        
        Demonstrates camera tracking techniques in 3D space:
        - Relative positioning using vector operations
        - View angle maintenance for better visual experience
        - Smooth following behavior through direct position updates
        """
        # Position camera behind and slightly above the aircraft
        # Uses vector operations from the camera's perspective
        camera.position = self.plane.position - camera.forward * 20 + camera.up * 5
        
        # Sync camera rotation with plane rotation for immersive view
        camera.rotation = self.plane.rotation
    
    def render_overlay(self):
        """
        Updates the UI elements based on current flight parameters.
        """
        # Elevator bar (original)
        normalized_elevator = -self.elevator / 10
        self.elevator_bar_fill.scale_y = 0.9 * abs(normalized_elevator)
        self.elevator_bar_fill.position = (0, 0.9 * normalized_elevator / 2)

        # Aileron bar
        normalized_aileron = -self.aileron / 10
        self.aileron_bar_fill.scale_y = 0.9 * abs(normalized_aileron)
        self.aileron_bar_fill.position = (0, 0.9 * normalized_aileron / 2)

        # Rudder bar
        normalized_rudder = -self.rudder / 10
        self.rudder_bar_fill.scale_y = 0.9 * abs(normalized_rudder)
        self.rudder_bar_fill.position = (0, 0.9 * normalized_rudder / 2)

        # Vertical velocity bar
        # Scale vertical velocity (state_long[1]) to a reasonable display range
        # Adjust divisor based on expected vv range
        if self.state_long.getmatrix()[1][0] < 0:
            normalized_vv = 1 / (-0.001 * self.state_long.getmatrix()[1][0] + 2) - 0.5
        else:
            normalized_vv = - 1 / (0.001 * self.state_long.getmatrix()[1][0] + 2) + 0.5 
        self.vv_bar_fill.scale_y = 0.9 * abs(normalized_vv)
        self.vv_bar_fill.position = (0, 0.9 * normalized_vv / 2)

        # Calculate altitude (y position above ground level)
        altitude = self.plane.y - self.ground_y # Offset by ground level position
        
        # Add warning for low altitude (change text color when below 100m)
        if altitude < 75:
            self.altitude_text.color = color.red
        else:
            self.altitude_text.color = color.white
            
        self.altitude_text.text = f'Altitude: {int(altitude)} m'

    def update_data(self):
        """
        Updates data for postflight graphs.
        """
        self.time_data.append(self.flight_time)
        self.aoa_data.append(self.state_long.getmatrix()[1][0])  # Angle of Attack in degrees
        cruise_speed = self.A.getmatrix()[1][2]
        self.velocity_data.append(self.state_long.getmatrix()[0][0] + cruise_speed)  # Total velocity
        # Approximate G-force as vertical acceleration (dv/dt) / 9.81
        if len(self.velocity_data) > 1:
            dv_dt = (self.velocity_data[-1] - self.velocity_data[-2]) / self.dt
            g_force = dv_dt / 9.81  # Assuming vertical component dominates
        else:
            g_force = 0
        self.gforce_data.append(g_force)
        self.altitude_data.append(self.plane.y - self.ground_y)  # Altitude above ground
        
        
    def end_simulation(self):
        """
        Cleans up resources and transitions to post-flight analysis.
        """
        global flight_time, crashed
        
        flight_time = self.flight_time
        
        # Record crash status for post-flight analysis
        crashed = self.crashed

        # Store data for post-flight analysis
        self.flight_data = {
            'selected_plane': self.selected_plane,
            'crashed': self.crashed,
            'time': self.time_data,
            'aoa': self.aoa_data,
            'velocity': self.velocity_data,
            'gforce': self.gforce_data,
            'altitude': self.altitude_data}
        
        # Clean up all entities including menu elements and ground
        destroy(self.plane)
        destroy(self.sky)
        destroy(self.ground)
        
        # Clean up UI elements
        destroy(self.instructions)
        destroy(self.altitude_text)
        destroy(self.elevator_bar_bg)
        destroy(self.aileron_bar_bg)
        destroy(self.rudder_bar_bg)
        destroy(self.vv_bar_bg)
        destroy(self.menu_panel)
        destroy(self.input_handler)
        
        # Clean up crash-specific elements if they exist
        if self.crash_message:
            destroy(self.crash_message)
            destroy(self.continue_button)
        
        # Transition to post-flight analysis
        PostFlight(self.flight_data)

# ---------------------------
#    WEATHER EFFECTS  
# ---------------------------
class Weather:
    """
    Crosswinds modifier to physics
    """
    def __init__(self):
        self.maxcrosswind = 8.0
        self.wind_x = 0.0

    def randomWind(self):
        self.wind_x = random.uniform(-self.maxcrosswind, self.maxcrosswind)
        # random windspeed between -maxcrosswind and maxcrosswind
        return self.wind_x
    def calmWind(self):
        self.wind_x = 0.0
        # way to restore calm skies
        return self.wind_x
    
# ---------------------------
#   POST-FLIGHT ANALYTICS
# ---------------------------
class PostFlight(Entity):
    def __init__(self, flight_data = None):
        super().__init__()
        self.flight_data = flight_data
        title_y = 0.4
        stats_y = 0.325
        graph_y = 0.05
        message_y = -0.225
        
        self.title = Text(text = 'Post-Flight Analytics',
                          position = (0, title_y),
                          scale = (2, 2),
                          origin = (0, 0))

        # Display flight time
        global flight_time, current_user, crashed
        minutes_to_add = flight_time / 60  # Convert seconds to minutes
        
        self.flight_time_text = Text(
            text = f'Flight Time: {flight_time:.2f} seconds',
            position = (0, stats_y), origin = (0, 0))
        
        # Initialize level-up related attributes
        self.level_up = False
        self.level_down = False
        self.new_level = current_user.level if current_user else 1
        self.new_total_minutes = 0
        
        # Update user's flight minutes and check for level up
        if current_user:
            user_manager = UserManager()

            # Update flight minutes
            self.new_total_minutes = user_manager.update_flight_minutes(current_user.user_id, minutes_to_add)
            # Update the currentuser object so that menu is always up to date with DB
            current_user.flight_minutes = self.new_total_minutes
            # Total minutes needed for levels 1-10
            required_minutes = [0, 2, 4, 7, 10, 13, 16, 19, 22, 25] 
            
            # Handle crash penalty
            if crashed and current_user.level > 1:
                self.level_down = True
                self.new_level = user_manager.update_level(current_user.user_id, current_user.level - 1)
            elif not crashed and minutes_to_add >=  1:  # Require at least 1 minute of flight time to level up
                # Check if total minutes qualify for the next level
                next_level = current_user.level + 1
                if next_level <= 10 and self.new_total_minutes >=  required_minutes[next_level - 1]:
                    self.level_up = True
                    self.new_level = user_manager.update_level(current_user.user_id, next_level)
                    
            # Update current_user.level
            current_user.level = self.new_level
            
            # Display level information
            self.level_text = Text(
                text = f'Current Pilot Level: {current_user.level}',
                position = (0.5, stats_y),
                origin = (0, 0))
            
            self.total_time_text = Text(
                text = f'Total Flight Minutes: {self.new_total_minutes:.2f}',
                position = (-0.5, stats_y),
                origin = (0, 0))
            
            if self.level_up:
                self.level_up_text = Text(
                    text = f'CONGRATULATIONS! You\'ve reached Level {self.new_level}!',
                    position = (0, message_y), origin = (0, 0), color = color.yellow)
                
            elif self.level_down:
                self.level_down_text = Text(
                    text = f'Crash Detected! Level decreased to {self.new_level}',
                    position = (0, message_y), origin = (0, 0), color = color.red.tint(-0.2))
                
            elif current_user.level < 10:
                # Show progress to next level
                minutes_to_next = required_minutes[current_user.level] - self.new_total_minutes
                if minutes_to_next < 0:
                    minutes_to_next = 0
                self.progress_text = Text(
                    text = f'Minutes to next level: {minutes_to_next:.2f}',
                    position = (0, message_y), origin = (0, 0))
        
        # Navigation buttons
        self.menu_button = Button(text = 'Return to Main Menu', position = (0, -0.3), scale = (0.35, 0.05))
        self.menu_button.on_click = self.return_to_menu
        self.quit_button = Button(text = 'Quit', position = (0, -0.4), scale = (0.25, 0.05))
        self.quit_button.on_click = application.quit

       # export button
        self.export_button = Button(text='Export Flight Log', position=(0, -0.2), scale=(0.3, 0.05))
        self.export_button.on_click = self.export_flight_log
        self.export_status_text = Text(text='', position=(0, -0.15), origin=(0, 0), scale=1)

        if flight_data:
            self.generate_graphs(flight_data, graph_y)

    def generate_graphs(self, flight_data, graph_y):
        """
        Generate four graphs side by side using Matplotlib and display them within Ursina UI.
        """
        graph_size = 1.7  # Graph display size in Ursina
        time = flight_data['time']
        
        plot_data = [
            (flight_data['aoa'], 'b-', 'Angle of Attack', 'AoA (deg)'),
            (flight_data['velocity'], 'g-', 'Velocity', 'Velocity (m/s)'),
            (flight_data['gforce'], 'r-', 'G-Force', 'G-Force (g)'),
            (flight_data['altitude'], 'm-', 'Altitude', 'Altitude (m)')] # Plot data: (data, color, title, y-label)
        
        fig, axs = pyplot.subplots(1, 4, figsize=(16, 4))  # 1 row, 4 columns
        fig.suptitle('Flight Performance Analysis', fontsize=16)

        # Configure each subplot
        for i in range(len(plot_data)):
            data, color, title, ylabel = plot_data[i]
            axs[i].plot(time, data, color, label=title)
            axs[i].set_title(title)
            axs[i].set_xlabel('Time (s)')
            axs[i].set_ylabel(ylabel)
            axs[i].grid(True)

        pyplot.tight_layout(rect=[0, 0, 1, 0.95])  # Adjust layout
        temp_file = 'temp_graphs.png'
        pyplot.savefig(temp_file, format='png', dpi=300)  # Save plot
        pyplot.close(fig)  # Free memory

        graph_texture = Texture(temp_file)  # Load as texture
        self.graph_entity = Entity(
            parent = camera.ui, 
            model = 'quad',
            texture = graph_texture,
            scale = (graph_size, graph_size/4),  # Match figsize aspect ratio
            position = (0, graph_y),
            z = -1)  # Render behind UI elements
        def export_flight_log(self):
          if not self.flight_data:
              self.export_status_text.text = 'No flight data to export.'
              return
  
          global current_user, flight_time, crashed
  
          export_dir = Path('exports')
          export_dir.mkdir(parents=True, exist_ok=True)
  
          ts = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%SZ')
          username_safe = (current_user.username if current_user else 'guest').replace(' ', '_')
          plane_safe = str(self.flight_data.get('selected_plane', 'unknown')).replace(' ', '_')
          base = f'flight_{ts}_{username_safe}_{plane_safe}'
  
          json_path = export_dir / f'{base}.json'
          csv_path = export_dir / f'{base}.csv'
          graph_path = export_dir / f'{base}_graphs.png'
  
          meta = {
              'exported_at_utc': ts,
              'username': current_user.username if current_user else None,
              'user_id': current_user.user_id if current_user else None,
              'pilot_level': current_user.level if current_user else None,
              'selected_plane': self.flight_data.get('selected_plane'),
              'flight_time_seconds': float(flight_time),
              'crashed': bool(crashed),
          }
  
          payload = {
              'meta': meta,
              'telemetry': {
                  'time': self.flight_data.get('time', []),
                  'aoa': self.flight_data.get('aoa', []),
                  'velocity': self.flight_data.get('velocity', []),
                  'gforce': self.flight_data.get('gforce', []),
                  'altitude': self.flight_data.get('altitude', []),
              },
          }
  
          json_path.write_text(json.dumps(payload, indent=2), encoding='utf-8')
  
          time_series = payload['telemetry']['time']
          aoa_series = payload['telemetry']['aoa']
          vel_series = payload['telemetry']['velocity']
          gf_series = payload['telemetry']['gforce']
          alt_series = payload['telemetry']['altitude']
  
          row_count = min(len(time_series), len(aoa_series), len(vel_series), len(gf_series), len(alt_series))
          with csv_path.open('w', newline='', encoding='utf-8') as f:
              # writting csv
              writer = csv.writer(f)
              writer.writerow(['time_s', 'aoa_deg', 'velocity', 'gforce_g', 'altitude_m'])
              for i in range(row_count):
                  writer.writerow([time_series[i], aoa_series[i], vel_series[i], gf_series[i], alt_series[i]])
  
          if getattr(self, 'graph_png_path', None) and Path(self.graph_png_path).exists():
              try:
                  shutil.copyfile(self.graph_png_path, graph_path)
              except OSError:
                  pass
  
          self.export_status_text.text = f'Exported to: {export_dir.as_posix()}/{base}.*'
      
        
    def return_to_menu(self):
        destroy(self.title)
        destroy(self.flight_time_text)
        
        if current_user:    # Destroy level-related texts if they exist
            destroy(self.level_text)
            destroy(self.total_time_text)
            if self.level_up:
                destroy(self.level_up_text)
            elif self.level_down:
                destroy(self.level_down_text)
            else:
                destroy(self.progress_text)
        
        destroy(self.menu_button)
        destroy(self.quit_button)
        destroy(self.export_button)
        destroy(self.export_status_text)
        destroy(self.graph_entity)
        
        # Reset flight statistics for next session
        global flight_time, crashed
        flight_time = 0
        crashed = False
        MainMenu()

#############################################################
####################### PROGRAM ENTRY #######################
#############################################################
        
if __name__  ==  '__main__':
    user_manager = UserManager()
    LoginScreen(user_manager = user_manager)
    app.run()
