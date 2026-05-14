# -*- coding: utf-8 -*-

__author__ = 'Brett Feltmate'

import klibs
from klibs import EL_GAZE_POS, P
from klibs.KLBoundary import CircleBoundary
from klibs.KLConstants import EL_SACCADE_END
from klibs.KLGraphics import fill, flip, blit, clear
from klibs.KLGraphics import KLDraw as kld
from klibs.KLUtilities import deg_to_px, pump
from klibs.KLUserInterface import any_key, ui_request, smart_sleep
from klibs.KLCommunication import message
from klibs.KLExceptions import TrialException
from klibs.KLGraphics.KLNumpySurface import NumpySurface

# typo prophylactics
LEFT = 'left'
RIGHT = 'right'
CENTER = 'center'
TARGET_LOC = 'target_location'
CUE_TYPE = 'cue_type'
TARGET = 'target'
NONTARGET = 'nontarget'
CUE = 'cue'
CUE_VALIDITY = 'cue_validity'
CUED_SIDE = 'cued_side'
CUE_ON = 'cue_on'
CUE_OFF = 'cue_off'
TARGET_ON = 'target_on'
TRIAL_END = 'trial_end'
SACCADE_RT = 'saccade_rt'
SACCADE_RESP = 'saccade_resp'
NA = 'NA'
BLOCK_NUM = 'block_num'
TRIAL_NUM = 'trial_num'
PRACTICING = 'practicing'
CONDITION = 'condition'
REMAIN = 'remain'
REMOVE = 'remove'

WHITE = (255, 255, 255, 255)


class GazeCueAgency(klibs.Experiment):
    def setup(self):

        offset_px = deg_to_px(P.offset)  # type: ignore[attr]

        self.locs = {
            LEFT: (P.screen_c[0] - offset_px, P.screen_c[1]),  # type: ignore[attr]
            RIGHT: (P.screen_c[0] + offset_px, P.screen_c[1]),  # type: ignore[attr]
            CENTER: P.screen_c,
        }

        self.tone = Tone(P.tone_duration, P.tone_type)  # type: ignore[attr]
        self.cues = {}

        # for cue_type in self.exp_factors.get('cue_type', NA):  # type: ignore[attr]
        for cue_type in self.trial_factory.exp_factors['cue_type']:  # type: ignore[attr]

            self.cues[cue_type] = {}

            for cued_side in self.trial_factory.exp_factors['cued_side']:  # type: ignore[attr]

                self.cues[cue_type][cued_side] = NumpySurface(
                    content=f'{P.image_dir}/{cue_type}-{cued_side}.png',
                    width=deg_to_px(P.cue_frame_width),  # type: ignore[attr]
                    height=deg_to_px(P.cue_frame_height),  # type: ignore[attr]
                )

        self.target = kld.Asterisk(
            size=deg_to_px(P.target_size),  # type: ignore[attr]
            thickness=deg_to_px(P.target_thick),  # type: ignore[attr]
            fill=WHITE,
        )

        self.el.add_boundaries(  # type: ignore[attr]
            boundaries=[
                CircleBoundary(
                    'left',
                    center=self.locs[LEFT],
                    radius=deg_to_px(P.boundary_radius),  # type: ignore[attr]
                ),
                CircleBoundary(
                    'right',
                    center=self.locs[RIGHT],
                    radius=deg_to_px(P.boundary_radius),  # type: ignore[attr]
                ),
                CircleBoundary(
                    'center',
                    center=self.locs[CENTER],
                    radius=deg_to_px(max(P.cue_frame_width, P.cue_frame_height) / 2),  # type: ignore[attr]
                ),
            ]
        )
        
        if P.run_practice_blocks:
            self.insert_practice_blocks([1], P.trials_per_practice_block)

    def block(self):
        fill()
        message(
            'Instructions needed; any key to start block.',
            registration=5,
            location=P.screen_c,
            blit_txt=True,
        )
        flip()

        any_key()

    def trial_prep(self):
        self.trial_deets = {}
        self.trial_deets[PRACTICING] = P.practicing  # type: ignore[attr]
        self.trial_deets[CONDITION] = P.condition  # type: ignore[attr]
        self.trial_deets[CUE_TYPE] = self.cue_type  # type: ignore[attr]
        self.trial_deets[CUED_SIDE] = self.cued_side  # type: ignore[attr]
        self.trial_deets[TARGET_LOC] = self.target_location  # type: ignore[attr]
        self.trial_deets[BLOCK_NUM] = P.block_number  # type: ignore[attr]
        self.trial_deets[TRIAL_NUM] = P.trial_number  # type
        self.trial_deets[SACCADE_RT] = None
        self.trial_deets[SACCADE_RESP] = None

        self.evm.add_event(CUE_ON, P.cue_onset)  # type: ignore[attr]

        if self.trial_deets[CONDITION] == REMOVE:
            self.evm.add_event(CUE_OFF, P.cue_duration, after=CUE_ON)  # type: ignore[attr]

        self.evm.add_event(TARGET_ON, P.cue_target_asynchrony, after=CUE_ON)  # type: ignore[attr]
        self.evm.add_event(TRIAL_END, P.response_window, after=TARGET_ON)  # type: ignore[attr]

        self.el.drift_correct(  # type: ignore[attr]
            target=self.cues[self.trial_deets[CUE_TYPE]]['neutral']
        )

    def trial(self):

        while self.evm.before(CUE_ON):
            self.fixation_check()

        self.draw(CUE_ON)
        self.tone.play()

        if self.trial_deets[CONDITION] == REMOVE:  # type: ignore[attr]

            while self.evm.before(CUE_OFF):
                self.fixation_check()

            self.draw(CUE_OFF)

        while self.evm.before(TARGET_ON):
            self.fixation_check()

        self.draw(TARGET_ON)

        el_now = self.el.now()  # type: ignore[attr]

        saccade = False

        while not saccade and self.evm.before(TRIAL_END):
            saccade = self.saccade_check()

        if saccade:
            self.trial_deets[SACCADE_RESP] = saccade.get('label')
            self.trial_deets[SACCADE_RT] = saccade.get('end_time') - el_now
        else:
            fill()
            message(
                'No response detected.', registration=5, location=P.screen_c
            )
            flip()
            smart_sleep(1000)

        return self.trial_deets

    def trial_clean_up(self):
        clear()
        smart_sleep(P.post_response_window)  # type: ignore[attr]

    def clean_up(self):
        pass

    def draw(self, what=None):
        fill()

        if what == CUE_ON:

            self.el.write(CUE_ON)  # type: ignore[attr]

            blit(
                self.cues[self.trial_deets[CUE_TYPE]][
                    self.trial_deets[CUED_SIDE]
                ],
                location=self.locs[CENTER],
                registration=5,
            )

        if what == CUE_OFF:

            self.el.write(CUE_OFF)  # type: ignore[attr]

        if what == TARGET_ON:

            self.el.write(TARGET_ON)  # type: ignore[attr]

            blit(
                self.target,
                location=self.locs[self.trial_deets[TARGET_LOC]],
                registration=5,
            )

        flip()

    def saccade_check(self):
        el_q = self.el.get_event_queue()  # type: ignore[attr]

        saccade_to_target = self.el.within_boundary(  # type: ignore[attr]
            self.trial_deets[TARGET_LOC],
            event_queue=el_q,
            valid_events=[EL_SACCADE_END],
        )

        saccade_to_nontarget = self.el.within_boundary(  # type: ignore[attr]
            LEFT if self.trial_deets[TARGET_LOC] == RIGHT else RIGHT,
            event_queue=el_q,
            valid_events=[EL_SACCADE_END],
        )

        if saccade_to_target and saccade_to_nontarget:
            raise RuntimeError(
                'Saccades to both target and nontarget detected'
            )

        if saccade_to_target:
            self.el.write('saccade_to_target')  # type: ignore[attr]
            return {'label': TARGET, 'end_time': saccade_to_target}

        if saccade_to_nontarget:
            self.el.write('saccade_to_nontarget')  # type: ignore[attr]
            return {'label': NONTARGET, 'end_time': saccade_to_nontarget}

        return False

    def fixation_check(self):
        # return True
        kb_q = pump(True)
        el_q = self.el.get_event_queue()  # type: ignore[attr]

        ui_request(queue=kb_q)

        if not self.el.within_boundary(CENTER, event_queue=el_q, valid_events=[EL_GAZE_POS]):  # type: ignore[attr]
            self.el.write('early_fixation_break')  # type: ignore[attr]

            fill()
            message(
                'Keep your gaze on the face until the target appears.',
                registration=5,
                location=P.screen_c,
            )
            flip()

            smart_sleep(1000)
            raise TrialException('early_fixation_break')
