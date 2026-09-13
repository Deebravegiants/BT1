# [H] CVE-2020-12861

## Summary
Severity: High
Advisory: CVE-2020-12861
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-06-24
Source: https://osv.dev/vulnerability/CVE-2020-12861
Type: osv

## Details
A heap buffer overflow in SANE Backends before 1.0.30 allows a malicious device connected to the same local network as the victim to execute arbitrary code, aka GHSL-2020-080.

## References
- http://packetstormsecurity.com/files/172841/SANE-Backends-Memory-Corruption-Code-Execution.html
- http://lists.opensuse.org/opensuse-security-announce/2020-10/msg00079.html
- http://lists.opensuse.org/opensuse-security-announce/2020-11/msg00003.html
- https://usn.ubuntu.com/4470-1/
- https://alioth-lists.debian.net/pipermail/sane-announce/2020/000041.html
- https://securitylab.github.com/advisories/GHSL-2020-075-libsane
