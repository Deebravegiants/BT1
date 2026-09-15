# [M] ALPINE-CVE-2026-25645

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-25645
Ecosystem: Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2026-03-25
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-25645
Type: osv

## Affected
- Alpine:v3.20: `py3-requests` — affected >=0 <2.33.1-r0
- Alpine:v3.21: `py3-requests` — affected >=0 <2.33.1-r0
- Alpine:v3.22: `py3-requests` — affected >=0 <2.33.1-r0
- Alpine:v3.23: `py3-requests` — affected >=0 <2.33.1-r0
- Alpine:v3.24: `py3-requests` — affected >=0 <2.33.1-r0

## Details
Requests is a HTTP library. Prior to version 2.33.0, the `requests.utils.extract_zipped_paths()` utility function uses a predictable filename when extracting files from zip archives into the system temporary directory. If the target file already exists, it is reused without validation. A local attacker with write access to the temp directory could pre-create a malicious file that would be loaded in place of the legitimate one. Standard usage of the Requests library is not affected by this vulnerability. Only applications that call `extract_zipped_paths()` directly are impacted. Starting in version 2.33.0, the library extracts files to a non-deterministic location. If developers are unable to upgrade, they can set `TMPDIR` in their environment to a directory with restricted write access.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-25645
