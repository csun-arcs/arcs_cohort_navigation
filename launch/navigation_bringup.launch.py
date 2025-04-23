import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument, ExecuteProcess
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PythonExpression
from launch_ros.actions import Node


def generate_launch_description():
    # Package and file paths
    nav_pkg = "arcs_cohort_navigation"
    nav_pkg_share_dir = get_package_share_directory(nav_pkg)

    # Defaults
    default_ekf_params_file_template = os.path.join(
        nav_pkg_share_dir, "config", "ekf_params.yaml.template"
    )
    default_ekf_params_file = os.path.join(
        nav_pkg_share_dir, "config", "ekf_params.yaml"
    )
    default_slam_params_file_template = os.path.join(
        nav_pkg_share_dir, "config", "slam_params.yaml.template"
    )
    default_slam_params_file = os.path.join(
        nav_pkg_share_dir, "config", "slam_params.yaml"
    )
    default_nav2_params_file_template = os.path.join(
        nav_pkg_share_dir, "config", "nav2_mppi_stamped_params.yaml.template"
    )
    default_nav2_params_file = os.path.join(
        nav_pkg_share_dir, "config", "nav2_params.yaml"
    )
    default_log_level = "INFO"

    # Declare launch arguments
    declare_namespace_arg = DeclareLaunchArgument(
        "ns",
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
    declare_use_ekf_params_template_arg = DeclareLaunchArgument(
        "use_ekf_params_template",
        default_value="true",
        description="If true, generate the EKF params from the specified EKF params template.",
    )
    declare_use_slam_params_template_arg = DeclareLaunchArgument(
        "use_slam_params_template",
        default_value="true",
        description="If true, generate the SLAM params from the specified SLAM params template.",
    )
    declare_use_nav2_params_template_arg = DeclareLaunchArgument(
        "use_nav2_params_template",
        default_value="true",
        description="If true, generate the Nav2 params from the specified Nav2 params template.",
    )
    declare_ekf_params_template_arg = DeclareLaunchArgument(
        "ekf_params_template",
        default_value=default_ekf_params_file_template,
        description="Path to the params file template from which to generate the params file for the robot_localization package EKF node.",
    )
    declare_ekf_params_arg = DeclareLaunchArgument(
        "ekf_params",
        default_value=default_ekf_params_file,
        description="Path to the params file to load for the robot_localization package EKF node.",
    )
    declare_slam_params_template_arg = DeclareLaunchArgument(
        "slam_params_template",
        default_value=default_slam_params_file_template,
        description="Path to the params file template from which to generate the params file for the slam_toolbox package SLAM node.",
    )
    declare_slam_params_arg = DeclareLaunchArgument(
        "slam_params",
        default_value=default_slam_params_file,
        description="Path to the params file to load for the slam_toolbox package SLAM node.",
    )
    declare_nav2_params_template_arg = DeclareLaunchArgument(
        "nav2_params_template",
        default_value=default_nav2_params_file_template,
        description="Path to the params file template from which to generate the params file for the nav2_bringup package Nav2 bringup launcher.",
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

    # Launch configurations
    namespace = LaunchConfiguration("ns")
    prefix = LaunchConfiguration("prefix")
    use_sim_time = LaunchConfiguration("use_sim_time")
    use_ekf = LaunchConfiguration("use_ekf")
    use_slam = LaunchConfiguration("use_slam")
    use_nav2 = LaunchConfiguration("use_nav2")
    use_ekf_params_template = LaunchConfiguration("use_ekf_params_template")
    use_slam_params_template = LaunchConfiguration("use_slam_params_template")
    use_nav2_params_template = LaunchConfiguration("use_nav2_params_template")
    ekf_params_template = LaunchConfiguration("ekf_params_template")
    ekf_params = LaunchConfiguration("ekf_params")
    slam_params_template = LaunchConfiguration("slam_params_template")
    slam_params = LaunchConfiguration("slam_params")
    nav2_params_template = LaunchConfiguration("nav2_params_template")
    nav2_params = LaunchConfiguration("nav2_params")
    log_level = LaunchConfiguration("log_level")

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

    # Generate EKF params from template.
    # The prefix will be substituted into the template in
    # place of the ARCS_COHORT_PREFIX variable and the namespace will be
    # substituted in place of ARCS_COHORT_NAMESPACE.
    ekf_params_generator = ExecuteProcess(
        condition=IfCondition(use_ekf_params_template),
        cmd=[
            [
                "ARCS_COHORT_PREFIX='",
                prefix_,
                "' ",
                "ARCS_COHORT_NAMESPACE='",
                namespace_,
                "' ",
                "envsubst < ",
                ekf_params_template,
                " > ",
                ekf_params,
            ]
        ],
        shell=True,
        output="screen",
    )

    # Generate SLAM params from template.
    # The prefix will be substituted into the template in
    # place of the ARCS_COHORT_PREFIX variable and the namespace will be
    # substituted in place of ARCS_COHORT_NAMESPACE.
    slam_params_generator = ExecuteProcess(
        condition=IfCondition(use_slam_params_template),
        cmd=[
            [
                "ARCS_COHORT_PREFIX='",
                prefix_,
                "' ",
                "ARCS_COHORT_NAMESPACE='",
                namespace_,
                "' ",
                "envsubst < ",
                slam_params_template,
                " > ",
                slam_params,
            ]
        ],
        shell=True,
        output="screen",
    )

    # Generate Nav2 params from template.
    # The prefix will be substituted into the template in
    # place of the ARCS_COHORT_PREFIX variable and the namespace will be
    # substituted in place of ARCS_COHORT_NAMESPACE.
    nav2_params_generator = ExecuteProcess(
        condition=IfCondition(use_nav2_params_template),
        cmd=[
            [
                "ARCS_COHORT_PREFIX='",
                prefix_,
                "' ",
                "ARCS_COHORT_NAMESPACE='",
                namespace_,
                "' ",
                "envsubst < ",
                nav2_params_template,
                " > ",
                nav2_params,
            ]
        ],
        shell=True,
        output="screen",
    )

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
                    get_package_share_directory(nav_pkg),
                    "launch",
                    "custom_nav2.launch.py",
                )
            ]
        ),
        launch_arguments={
            "params_file": nav2_params,
            "use_sim_time": use_sim_time,
        }.items(),
        condition=IfCondition(use_nav2),
    )

    return LaunchDescription(
        [
            # Declare arguments
            declare_namespace_arg,
            declare_prefix_arg,
            declare_use_sim_time_arg,
            declare_use_ekf_arg,
            declare_use_slam_arg,
            declare_use_nav2_arg,
            declare_use_ekf_params_template_arg,
            declare_use_slam_params_template_arg,
            declare_use_nav2_params_template_arg,
            declare_ekf_params_template_arg,
            declare_ekf_params_arg,
            declare_slam_params_template_arg,
            declare_slam_params_arg,
            declare_nav2_params_template_arg,
            declare_nav2_params_arg,
            declare_log_level_arg,
            # Param file generators
            ekf_params_generator,
            slam_params_generator,
            nav2_params_generator,
            # Nodes
            ekf_node,
            # Launchers
            slam_bringup_launch,
            nav2_bringup_launch,
        ]
    )
