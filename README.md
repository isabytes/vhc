# Vehicle Dynamics Simulator
1.0.0

## Description
This vehicle simulation game was developed as a final project for Code in Place 2024 by Stanford University.
It allows users to simulate and observe a diverse range of vehicles, from compact cars to large trucks, including both conventional and electric powertrains. The simulation includes realistic physics, gear shifting mechanisms, and performance metrics, demonstrating the practical application of fundamental Python concepts while also implementing more advanced techniques in specific areas to maintain realism.

## Dependencies
- Python 3.x
- Pygame
- NumPy

## How to Run
1. Clone this repository or download the source code.
2. Install the required dependencies.
3. Navigate to the `src` folder within the project directory.
4. Run the following command:
   ```
   python main.py
   ```

## Controls
- Select different vehicles or trailer weights from the menu.
- Use the on-screen buttons to start, pause, and restart the simulation.

## Features
- Multiple vehicle types with different engine characteristics 
- Visual representation of vehicles with rotating wheels
- Realistic physics calculations including aerodynamic drag, 
  engine force based on RPM and gear ratios, and mass-dependent acceleration
- Advanced gear shifting and clutch system simulation
- Detailed performance metrics (speed, RPM, acceleration times, emissions)
- Real-time graphical display of vehicle performance (RPM gauge, speedometer)
- Customizable trailer weights for trucks
- Interactive menu system for vehicle selection
- Support for both metric and imperial units

## Project Structure
- `main.py`: Entry point of the application
- `config.py`: Configurations for the vehicles
- `vehicle.py`: Core vehicle simulation logic
- `gear_shifting.py`: Gear shifting system 
- `drawing.py`: Rendering functions for the simulation
- `menu.py`: Menu system for vehicle selection and options
- `background.py`: Background rendering and scrolling


## License
Vehicle Dynamics Simulator was created as a final project for Code in Place 2024 by Stanford University. This project is intended for educational purposes and is provided as-is, without any warranty. You are welcome to view, use, and learn from this code.If you use or adapt this project, please credit it as "Vehicle Dynamics Simulator from Code in Place 2024" and link to this repository. For any questions or concerns please submit an issue through this repository's GitHub Issues page or contact the repository owner via isabytes on GitHub.

