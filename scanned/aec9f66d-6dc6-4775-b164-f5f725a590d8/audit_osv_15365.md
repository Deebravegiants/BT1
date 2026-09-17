# [C] CVE-2019-15683

## Summary
Severity: Critical
Advisory: CVE-2019-15683
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-10-29
Source: https://osv.dev/vulnerability/CVE-2019-15683
Type: osv

## Details
TurboVNC server code contains stack buffer overflow vulnerability in commit prior to cea98166008301e614e0d36776bf9435a536136e. This could possibly result into remote code execution, since stack frame is not protected with stack canary. This attack appear to be exploitable via network connectivity. To exploit this vulnerability authorization on server is required. These issues have been fixed in commit cea98166008301e614e0d36776bf9435a536136e.

## References
- https://github.com/TurboVNC/turbovnc/commit/cea98166008301e614e0d36776bf9435a536136e
