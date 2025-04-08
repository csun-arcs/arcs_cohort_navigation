import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

def generate_launch_description():
    # Package and file paths
    pkg_nav = 'arcs_cohort_navigation'

    # Paths to default files
    default_ekf_params = os.path.join(
        get_package_share_directory(pkg_nav),
        'config',
        'ekf_params.yaml'
    )
    default_slam_params = os.path.join(
        get_package_share_directory(pkg_nav),
        'config',
        'slam_params.yaml'
    )
    default_nav2_params = os.path.join(
        get_package_share_directory(pkg_nav),
        'config',
        'nav2_params.yaml'
    )

    # Declare launch arguments
    declare_use_sim_time_cmd = DeclareLaunchArgument(
        "use_sim_time", default_value="true", description="Use simulation time"
    )
    declare_ekf_params_cmd = DeclareLaunchArgument(
        "ekf_params",
        default_value=default_ekf_params,
        description="Path to the params file to load for the robot_localization package EKF node",
    )
    declare_slam_params_cmd = DeclareLaunchArgument(
        "slam_params",
        default_value=default_slam_params,
        description="Path to the params file to load for the slam_toolbox package SLAM node",
    )
    declare_nav2_params_cmd = DeclareLaunchArgument(
        "nav2_params",
        default_value=default_nav2_params,
        description="Path to the params file to load for the nav2_bringup package Nav2 bringup launcher",
    )
    declare_use_ekf_cmd = DeclareLaunchArgument(
        "use_ekf", default_value="true", description="Launch robot_localization package EKF node"
    )
    declare_use_slam_cmd = DeclareLaunchArgument(
        "use_slam", default_value="true", description="Launch slam_toolbox package SLAM node"
    )
    declare_use_nav2_cmd = DeclareLaunchArgument(
        "use_nav2", default_value="true", description="Launch nav2_bringup package Nav2 bringup launcher"
    )

    # Launch configurations
    use_sim_time = LaunchConfiguration("use_sim_time")
    ekf_params = LaunchConfiguration("ekf_params")
    slam_params = LaunchConfiguration("slam_params")
    nav2_params = LaunchConfiguration("nav2_params")
    use_ekf = LaunchConfiguration("use_ekf")
    use_slam = LaunchConfiguration("use_slam")
    use_nav2 = LaunchConfiguration("use_nav2")

    # robot_localization EKF node
    ekf_node = Node(
        condition=IfCondition(use_ekf),
        package='robot_localization',
        executable='ekf_node',
        name='ekf_filter_node',
        output='screen',
        parameters=[ekf_params]
    )

    # SLAM bringup launch
    slam_bringup_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            os.path.join(
                get_package_share_directory('slam_toolbox'),
                'launch',
                'online_async_launch.py'
            )
        ]),
        launch_arguments={
            'slam_params_file': slam_params,
            'use_sim_time': LaunchConfiguration('use_sim_time')
        }.items(),
        condition=IfCondition(use_slam),
    )

    # Nav2 bringup launch
    nav2_bringup_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            os.path.join(
                get_package_share_directory('nav2_bringup'),
                'launch',
                'bringup_launch.py'
            )
        ]),
        launch_arguments={
            'params_file': nav2_params,
            'use_sim_time': LaunchConfiguration('use_sim_time')
        }.items(),
        condition=IfCondition(use_nav2),
    )

    return LaunchDescription([
        declare_use_sim_time_cmd,
        declare_ekf_params_cmd,
        declare_slam_params_cmd,
        declare_nav2_params_cmd,
        declare_use_ekf_cmd,
        declare_use_slam_cmd,
        declare_use_nav2_cmd,
        ekf_node,
        slam_bringup_launch,
        nav2_bringup_launch,
    ])
