### Klibs Parameter overrides ###

#########################################
# Runtime Settings
#########################################
collect_demographics = True
manual_demographics_collection = False
manual_trial_generation = False
run_practice_blocks = True
multi_user = False
view_distance = (
    57  # in centimeters, 57cm = 1 deg of visual angle per cm of screen
)
allow_hidpi = True

#########################################
# Available Hardware
#########################################
eye_tracker_available = True
eye_tracking = True

#########################################
# Environment Aesthetic Defaults
#########################################
default_fill_color = (255, 255, 255, 255)
default_color = (0, 0, 0, 255)
default_font_size = 1
default_font_unit = 'deg'
default_font_name = 'Hind-Medium'

#########################################
# EyeLink Settings
#########################################
manual_eyelink_setup = False
manual_eyelink_recording = False

saccadic_velocity_threshold = 20
saccadic_acceleration_threshold = 5000
saccadic_motion_threshold = 0.15

#########################################
# Experiment Structure
#########################################
multi_session_project = False
trials_per_block = 120
blocks_per_experiment = 4
conditions = ['remain', 'remove']  # the gaze cue
default_condition = 'remain'

#########################################
# Development Mode Settings
#########################################
dm_auto_threshold = True
dm_trial_show_mouse = True
dm_ignore_local_overrides = False
dm_show_gaze_dot = True

#########################################
# Data Export Settings
#########################################
primary_table = 'trials'
unique_identifier = 'userhash'
exclude_data_cols = ['created']
append_info_cols = ['random_seed']
datafile_ext = '.txt'
append_hostname = False

#########################################
# PROJECT-SPECIFIC VARS
#########################################
trials_per_practice_block = 10

# degrees of visual angle
cue_frame_width = 16
cue_frame_height = 10
target_size = 1
target_thick = 0.2
boundary_radius = 2
offset = cue_frame_width // 2 + 4  # e.g., 4 dva from edge of cue frame

# event timings (ms)
cue_onset = 1000
cue_duration = 200
cue_target_asynchrony = 400
response_window = 1000
tone_duration = 100
post_response_window = 1000
tone_type = 'sine'
