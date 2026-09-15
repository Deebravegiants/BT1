# [M] CVE-2018-14332

## Summary
Severity: Medium
Advisory: CVE-2018-14332
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-07-19
Source: https://osv.dev/vulnerability/CVE-2018-14332
Type: osv

## Details
An issue was discovered in Clementine Music Player 1.3.1. Clementine.exe is vulnerable to a user mode write access violation due to a NULL pointer dereference in the Init call in the MoodbarPipeline::NewPadCallback function in moodbar/moodbarpipeline.cpp. The vulnerability is triggered when the user opens a malformed mp3 file.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-07/msg00038.html
- http://lists.opensuse.org/opensuse-security-announce/2019-08/msg00064.html
- https://github.com/MostafaSoliman/Security-Advisories/blob/master/CVE-2018-14332
- https://github.com/clementine-player/Clementine/blob/e5ab3e786f9adde12cec3cc90cfe8c1cc6b06320/src/moodbar/moodbarpipeline.cpp#L155
- https://github.com/clementine-player/Clementine/issues/6078
