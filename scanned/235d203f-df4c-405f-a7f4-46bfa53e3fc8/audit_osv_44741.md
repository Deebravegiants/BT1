# [C] SadTalker OS Command Injection via Audio Filename

## Summary
Severity: Critical
Advisory: CVE-2026-85696
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-04
Source: https://osv.dev/vulnerability/CVE-2026-85696
Type: osv

## Details
SadTalker contains an OS command injection vulnerability in the video muxing process where uploaded audio filenames are interpolated into ffmpeg commands without proper escaping. Attackers can upload audio files with shell metacharacters in the filename to break out of quoted arguments and execute arbitrary system commands when video generation occurs.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/85xxx/CVE-2026-85696.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-85696
- https://www.vulncheck.com/advisories/sadtalker-os-command-injection-via-audio-filename
- https://github.com/OpenTalker/SadTalker/issues/1043
- https://github.com/OpenTalker/SadTalker
- https://github.com/OpenTalker/SadTalker/blob/v0.0.2/src/utils/videoio.py
