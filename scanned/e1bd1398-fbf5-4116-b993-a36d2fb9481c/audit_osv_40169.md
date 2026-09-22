# [H] libvncclient Tight decoder has an attacker-controlled heap out-of-bounds write

## Summary
Severity: High
Advisory: CVE-2026-50538
Aliases: GHSA-v9pm-47h4-jcq8
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-08-21
Source: https://osv.dev/vulnerability/CVE-2026-50538
Type: osv

## Details
LibVNCClient is a library for easy implementation of a VNC client. In versions 0.9.12 through 0.9.15, a malicious (or man-in-the-middle) VNC server can force a connecting `libvncclient` to write attacker-controlled data past the end of its framebuffer. This is an out-of-bounds heap write with attacker-controlled length, contents, and offset. It needs no authentication (the attacker
is the server), works in a default build with default settings, and fires from a single `FramebufferUpdate` the moment the victim connects. It crashes any client unconditionally (denial of service); we also demonstrated it overwriting an application callback pointer and redirecting execution to attacker-chosen code (code execution) under the default configuration. Commit 540332be3e0acc566fa64da6f1b4680c72c724dd patches the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/50xxx/CVE-2026-50538.json
- https://github.com/LibVNC/libvncserver/security/advisories/GHSA-v9pm-47h4-jcq8
- https://nvd.nist.gov/vuln/detail/CVE-2026-50538
- https://github.com/LibVNC/libvncserver/commit/540332be3e0acc566fa64da6f1b4680c72c724dd
