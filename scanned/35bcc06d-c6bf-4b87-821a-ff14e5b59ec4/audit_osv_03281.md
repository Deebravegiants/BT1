# [H] ALPINE-CVE-2025-4330

## Summary
Severity: High
Advisory: ALPINE-CVE-2025-4330
Ecosystem: Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2025-06-03
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-4330
Type: osv

## Affected
- Alpine:v3.19: `python3` — affected >=0 <3.11.13-r0
- Alpine:v3.20: `python3` — affected >=0 <3.12.11-r0
- Alpine:v3.21: `python3` — affected >=0 <3.12.11-r0
- Alpine:v3.22: `python3` — affected >=0 <3.12.11-r0
- Alpine:v3.23: `python3` — affected >=0 <3.12.11-r0
- Alpine:v3.24: `python3` — affected >=0 <3.12.11-r0
- Alpine:v3.23: `python3-tkinter` — affected >=0 <3.12.11-r0
- Alpine:v3.24: `python3-tkinter` — affected >=0 <3.12.11-r0

## Details
Allows the extraction filter to be ignored, allowing symlink targets to point outside the destination directory, and the modification of some file metadata.


You are affected by this vulnerability if using the tarfile module to extract untrusted tar archives using TarFile.extractall() or TarFile.extract() using the filter= parameter with a value of "data" or "tar". See the tarfile  extraction filters documentation https://docs.python.org/3/library/tarfile.html#tarfile-extraction-filter  for more information.

Note that for Python 3.14 or later the default value of filter= changed from "no filtering" to `"data", so if you are relying on this new default behavior then your usage is also affected.

Note that none of these vulnerabilities significantly affect the installation of source distributions which are tar archives as source distributions already allow arbitrary code execution during the build process. However when evaluating source distributions it's important to avoid installing source distributions with suspicious links.

## References
- https://security.alpinelinux.org/vuln/CVE-2025-4330
