import main


def test_parse_args_does_not_require_time_for_picture_mode():
    options = main.parse_args(["-P", "-i", "image.jpg"])

    assert options.mode == "picture"
    assert options.input == "image.jpg"
    assert options.time == "00:00"


def test_parse_args_requires_output_for_video_mode():
    try:
        main.parse_args(["-V", "-i", "video.mp4"])
    except SystemExit as exc:
        assert exc.code != 0
    else:
        raise AssertionError("video mode without output should fail")
