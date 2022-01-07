import os

import pytest
import torch
from torchvision.io import _HAS_VIDEO_DECODER, VideoReader

try:
    import av
except ImportError:
    av = None

VIDEO_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "videos")

test_videos = [
    "RATRACE_wave_f_nm_np1_fr_goo_37.avi",
    "TrumanShow_wave_f_nm_np1_fr_med_26.avi",
    "v_SoccerJuggling_g23_c01.avi",
    "v_SoccerJuggling_g24_c01.avi",
    "R6llTwEh07w.mp4",
    "SOX5yA1l24A.mp4",
    "WUzgd7C1pWA.mp4",
]


@pytest.mark.skipif(_HAS_VIDEO_DECODER is False, reason="Didn't compile with support for gpu decoder")
class TestVideoGPUDecoder:
    @pytest.mark.skipif(av is None, reason="PyAV unavailable")
    def test_frame_reading(self):
        for test_video in test_videos:
            full_path = os.path.join(VIDEO_DIR, test_video)
            decoder = VideoReader(full_path, device="cuda:0")
            with av.open(full_path) as container:
                for av_frame in container.decode(container.streams.video[0]):
                    av_frames = torch.tensor(av_frame.to_ndarray().flatten())
                    vision_frames = next(decoder)["data"]
                    mean_delta = torch.mean(torch.abs(av_frames.float() - decoder._reformat(vision_frames).float()))
                    assert mean_delta < 0.1


if __name__ == "__main__":
    pytest.main([__file__])
