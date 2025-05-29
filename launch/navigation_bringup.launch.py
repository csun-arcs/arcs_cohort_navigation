import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument, LogInfo, GroupAction
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PythonExpression, TextSubstitution
from launch_ros.actions import Node, PushRosNamespace
from nav2_common.launch import ReplaceString


def generate_launch_description():
    # Package and file paths
    nav_pkg = "arcs_cohort_navigation"
    nav_pkg_share_dir = get_package_share_directory(nav_pkg)

    # Defaults
    default_scan_topic = "scan/merged/scan"
    default_pointcloud_topic = "camera/points/filtered/base"
    default_odom_topic = "odometry/filtered"
    default_local_costmap_plugins = TextSubstitution(
        text='["static_layer", "obstacle_layer", "voxel_layer", "inflation_layer"]'
    ),
    default_global_costmap_plugins = TextSubstitution(
        text='["static_layer", "obstacle_layer", "stvl_layer", "inflation_layer"]'
    ),
    default_ekf_params_file = os.path.join(
        nav_pkg_share_dir, "config", "ekf_params.yaml"
    )
    default_slam_params_file = os.path.join(
        nav_pkg_share_dir, "config", "slam_params.yaml"
    )
    default_nav2_params_file = os.path.join(
        nav_pkg_share_dir, "config", "nav2_mppi_stamped_params.yaml"
    )
    default_log_level = "INFO"

    # Declare launch arguments
    declare_namespace_arg = DeclareLaunchArgument(
        "namespace",
        default_value="",
        description="Namespace under which to bring up nodes, topics, etc.",
    )
    declare_prefix_arg = DeclareLaunchArgument(
        "prefix",
        default_value="",
        description=(
            "A prefix for the names of joints, links, etc. in the robot model). "
            "E.g. 'base_link' will become 'cohort1_base_link' if prefix "
            "is set to 'cohort1'."
        ),
    )
    declare_scan_topic_arg = DeclareLaunchArgument(
        "scan_topic",
        default_value=default_scan_topic,
        description="Laser scan topic to be used by navigation.",
    )
    declare_pointcloud_topic_arg = DeclareLaunchArgument(
        "pointcloud_topic",
        default_value=default_pointcloud_topic,
        description="Point cloud topic to be used by navigation.",
    )
    declare_odom_topic_arg = DeclareLaunchArgument(
        "odom_topic",
        default_value=default_odom_topic,
        description="Odometry topic to be used by navigation.",
    )
    declare_local_costmap_plugins_arg = DeclareLaunchArgument(
        "local_costmap_plugins",
        default_value=default_local_costmap_plugins,
        description="YAML-style list of plugins to use in the local costmap."
    )
    declare_global_costmap_plugins_arg = DeclareLaunchArgument(
        "global_costmap_plugins",
        default_value=default_global_costmap_plugins,
        description="YAML-style list of plugins to use in the global costmap."
    )
    declare_ekf_params_arg = DeclareLaunchArgument(
        "ekf_params",
        default_value=default_ekf_params_file,
        description="Path to the params file to load for the robot_localization package EKF node.",
    )
    declare_slam_params_arg = DeclareLaunchArgument(
        "slam_params",
        default_value=default_slam_params_file,
        description="Path to the params file to load for the slam_toolbox package SLAM node.",
    )
    declare_nav2_params_arg = DeclareLaunchArgument(
        "nav2_params",
        default_value=default_nav2_params_file,
        description="Path to the params file to load for the nav2_bringup package Nav2 bringup launcher.",
    )
    declare_log_level_arg = DeclareLaunchArgument(
        "log_level",
        default_value=default_log_level,
        description="Set the log level for nodes.",
    )
    declare_use_sim_time_arg = DeclareLaunchArgument(
        "use_sim_time", default_value="true", description="Use simulation time."
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

    # Launch configurations
    namespace = LaunchConfiguration("namespace")
    prefix = LaunchConfiguration("prefix")
    scan_topic = LaunchConfiguration("scan_topic")
    pointcloud_topic = LaunchConfiguration("pointcloud_topic")
    odom_topic = LaunchConfiguration("odom_topic")
    local_costmap_plugins = LaunchConfiguration("local_costmap_plugins")
    global_costmap_plugins = LaunchConfiguration("global_costmap_plugins")
    ekf_params = LaunchConfiguration("ekf_params")
    slam_params = LaunchConfiguration("slam_params")
    nav2_params = LaunchConfiguration("nav2_params")
    log_level = LaunchConfiguration("log_level")
    use_sim_time = LaunchConfiguration("use_sim_time")
    use_ekf = LaunchConfiguration("use_ekf")
    use_slam = LaunchConfiguration("use_slam")
    use_nav2 = LaunchConfiguration("use_nav2")

    # Log info
    log_info = LogInfo(msg=['Navigation bringup launching with namespace: ', namespace, ', prefix: ', prefix, ', local_costmap_plugins: ', local_costmap_plugins])

    # Use PushRosNamespace to apply the namespace to all nodes below
    push_namespace = PushRosNamespace(namespace=namespace)

    # Build the prefix with underscore.
    # This expression will evaluate to, for example, "cohort1_" if
    # the prefix is "cohort1", or to an empty string if prefix is empty.
    prefix_ = PythonExpression(
        ["'", prefix, "_' if '", prefix, "' else ''"]
    )

    # Build the namespace with slash
    # This expression will evaluate to, for example, "cohort1/" if
    # the namespace is "cohort1", or to an empty string if namespace is empty.
    namespace_ = PythonExpression(
        ["'", namespace, "/' if '", namespace, "' else ''"]
    )

    # Build the namespace with leading and trailing slashes.
    # This expression will evaluate to, for example, "/cohort1/" if
    # the namespace is "cohort1", or to an empty string if namespace is empty.
    _namespace_ = PythonExpression(
        ["'/", namespace, "/' if '", namespace, "' else ''"]
    )

    # Perform substitutions of <NAMESPACE> and <PREFIX> in EKF params file
    substituted_ekf_params = ReplaceString(
        source_file=ekf_params,
        replacements={
            '<NAMESPACE>': namespace,
            '<NAMESPACE_>': namespace_,
            '<_NAMESPACE_>': _namespace_,
            '<PREFIX>': prefix,
            '<PREFIX_>': prefix_,
            '<SCAN_TOPIC>': scan_topic,
            '<POINTCLOUD_TOPIC>': pointcloud_topic,
        }
    )

    # Perform substitutions of <NAMESPACE> and <PREFIX> in SLAM params file
    substituted_slam_params = ReplaceString(
        source_file=slam_params,
        replacements={
            '<NAMESPACE>': namespace,
            '<NAMESPACE_>': namespace_,
            '<_NAMESPACE_>': _namespace_,
            '<PREFIX>': prefix,
            '<PREFIX_>': prefix_,
            '<SCAN_TOPIC>': scan_topic,
            '<POINTCLOUD_TOPIC>': pointcloud_topic,
        }
    )

    # Perform substitutions of <NAMESPACE> and <PREFIX> in SLAM params file
    substituted_nav2_params = ReplaceString(
        source_file=nav2_params,
        replacements={
            '<NAMESPACE>': namespace,
            '<NAMESPACE_>': namespace_,
            '<_NAMESPACE_>': _namespace_,
            '<PREFIX>': prefix,
            '<PREFIX_>': prefix_,
            '<SCAN_TOPIC>': scan_topic,
            '<POINTCLOUD_TOPIC>': pointcloud_topic,
            '<ODOM_TOPIC>': odom_topic,
            '<LOCAL_COSTMAP_PLUGINS>': local_costmap_plugins,
            '<GLOBAL_COSTMAP_PLUGINS>': global_costmap_plugins,
        }
    )

    # robot_localization EKF node
    ekf_node = GroupAction([
        push_namespace,
        Node(
            condition=IfCondition(use_ekf),
            package="robot_localization",
            executable="ekf_node",
            name="ekf_filter_node",
            output="screen",
            parameters=[substituted_ekf_params],
            arguments=["--ros-args", "--log-level", log_level],
            remappings=[
                ("/tf", "tf"),
                ("/tf_static", "tf_static"),
            ],
        ),
    ])

    # Nav2 cmd_vel stamper launch
    nav2_teleop_stamper_node = GroupAction([
        push_namespace,
        Node(
            condition=IfCondition(use_nav2),
            package="twist_stamper",
            executable="twist_stamper",
            name="twist_stamper",
            remappings=[
                ('cmd_vel_in', 'cmd_vel_nav'),
                ('cmd_vel_out', 'diff_cont/cmd_vel'),
            ],
            parameters=[{"use_sim_time": use_sim_time}]
        ),
    ])

    # SLAM bringup launch
    slam_bringup_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            [
                os.path.join(
                    get_package_share_directory(nav_pkg),
                    "launch",
                    "slam.launch.py",
                )
            ]
        ),
        launch_arguments={
            "namespace": namespace,
            "slam_params_file": substituted_slam_params,
            "use_sim_time": use_sim_time,
        }.items(),
        condition=IfCondition(use_slam),
    )

    # Nav2 bringup launch
    nav2_bringup_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            [
                os.path.join(
                    get_package_share_directory(nav_pkg),
                    "launch",
                    "nav2.launch.py",
                )
            ]
        ),
        launch_arguments={
            "namespace": namespace,
            "params_file": substituted_nav2_params,
            "use_sim_time": use_sim_time,
        }.items(),
        condition=IfCondition(use_nav2),
    )

    return LaunchDescription(
        [
            # Declare arguments
            declare_namespace_arg,
            declare_prefix_arg,
            declare_scan_topic_arg,
            declare_pointcloud_topic_arg,
            declare_odom_topic_arg,
            declare_local_costmap_plugins_arg,
            declare_global_costmap_plugins_arg,
            declare_ekf_params_arg,
            declare_slam_params_arg,
            declare_nav2_params_arg,
            declare_log_level_arg,
            declare_use_sim_time_arg,
            declare_use_ekf_arg,
            declare_use_slam_arg,
            declare_use_nav2_arg,
            # Log info
            log_info,
            # Nodes
            ekf_node,
            nav2_teleop_stamper_node,
            # Launchers
            slam_bringup_launch,
            nav2_bringup_launch,
        ]
    )
