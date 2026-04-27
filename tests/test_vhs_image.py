from concurrent.futures import ThreadPoolExecutor

from src.VHSImage import generateVHSStyle


def test_generate_vhs_style_uses_isolated_temp_files(tmp_path):
    outputs = [tmp_path / "first.jpg", tmp_path / "second.jpg"]

    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = [
            executor.submit(
                generateVHSStyle,
                "assets/in-vhs.jpg",
                str(output),
                False,
                "2026/04/26",
                "20:27",
            )
            for output in outputs
        ]
        for future in futures:
            future.result()

    assert all(output.exists() for output in outputs)
