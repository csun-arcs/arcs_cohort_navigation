import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PythonExpression
from launch_ros.actions import Node


def generate_launch_description():
    # Package and file paths
    pkg_nav = "arcs_cohort_navigation"

    # Defaults
    default_ekf_params = os.path.join(
        get_package_share_directory(pkg_nav), "config", "ekf_params.yaml"
    )
    default_slam_params = os.path.join(
        get_package_share_directory(pkg_nav), "config", "slam_params.yaml"
    )
    default_nav2_dwb_stamped_params = os.path.join(
        get_package_share_directory(pkg_nav), "config", "nav2_dwb_stamped_params.yaml"
    )
    default_nav2_params = os.path.join(
        get_package_share_directory(pkg_nav), "config", "nav2_mppi_stamped_params.yaml"
    )
    default_log_level = "INFO"

    # Declare launch arguments
    declare_use_sim_time_arg = DeclareLaunchArgument(
        "use_sim_time", default_value="true", description="Use simulation time."
    )
    declare_ekf_params_arg = DeclareLaunchArgument(
        "ekf_params",
        default_value=default_ekf_params,
        description="Path to the params file to load for the robot_localization package EKF node.",
    )
    declare_slam_params_arg = DeclareLaunchArgument(
        "slam_params",
        default_value=default_slam_params,
        description="Path to the params file to load for the slam_toolbox package SLAM node.",
    )
    declare_use_dwb_params_arg = DeclareLaunchArgument(
        "use_dwb", default_value="false", description="Use DWB controller plugin"
    )
    declare_nav2_params_arg = DeclareLaunchArgument(
        "nav2_params",
        default_value=default_nav2_params,
        description="Path to the params file to load for the nav2_bringup package Nav2 bringup launcher.",
    )
    declare_use_ekf_arg = DeclareLaunchArgument(
        "use_ekf",
        default_value="true",
        description="Launch robot_localization package EKF node.",
    )
    declare_use_slam_arg = DeclareLaunchArgument(
        "use_slam",
        default_value="true",
        description="Launch slam_toolbox package SLAM node.",
    )
    declare_use_nav2_arg = DeclareLaunchArgument(
        "use_nav2",
        default_value="true",
        description="Launch nav2_bringup package Nav2 bringup launcher.",
    )
    declare_log_level_arg = DeclareLaunchArgument(
        "log_level",
        default_value=default_log_level,
        description="Set the log level for nodes.",
    )

    # Launch configurations
    use_sim_time = LaunchConfiguration("use_sim_time")
    ekf_params = LaunchConfiguration("ekf_params")
    slam_params = LaunchConfiguration("slam_params")
    use_dwb = LaunchConfiguration("use_dwb")
    nav2_params = LaunchConfiguration("nav2_params")
    use_ekf = LaunchConfiguration("use_ekf")
    use_slam = LaunchConfiguration("use_slam")
    use_nav2 = LaunchConfiguration("use_nav2")
    log_level = LaunchConfiguration("log_level")

    # robot_localization EKF node
    ekf_node = Node(
        condition=IfCondition(use_ekf),
        package="robot_localization",
        executable="ekf_node",
        name="ekf_filter_node",
        output="screen",
        parameters=[ekf_params],
        arguments=["--ros-args", "--log-level", log_level],
    )

    # SLAM bringup launch
    slam_bringup_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            [
                os.path.join(
                    get_package_share_directory("slam_toolbox"),
                    "launch",
                    "online_async_launch.py",
                )
            ]
        ),
        launch_arguments={
            "slam_params_file": slam_params,
            "use_sim_time": use_sim_time,
        }.items(),
        condition=IfCondition(use_slam),
    )

    # Nav2 bringup launch
    nav2_bringup_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            [
                os.path.join(
                    get_package_share_directory(pkg_nav),
                    "launch",
                    "custom_nav2.launch.py",
                )
            ]
        ),
        launch_arguments={
            "params_file": PythonExpression(
                [
                    '"',
                    default_nav2_dwb_stamped_params,
                    '" if "',
                    use_dwb,
                    '" == "true" else "',
                    nav2_params,
                    '"',
                ]
            ),
            "use_sim_time": use_sim_time,
        }.items(),
        condition=IfCondition(use_nav2),
    )

    return LaunchDescription(
        [
            # Declare arguments
            declare_use_sim_time_arg,
            declare_ekf_params_arg,
            declare_slam_params_arg,
            declare_use_dwb_params_arg,
            declare_nav2_params_arg,
            declare_use_ekf_arg,
            declare_use_slam_arg,
            declare_use_nav2_arg,
            declare_log_level_arg,
            # Nodes
            ekf_node,
            # Launchers
            slam_bringup_launch,
            nav2_bringup_launch,
        ]
    )
