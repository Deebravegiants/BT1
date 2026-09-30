# [C] CVE-2026-24061

## Summary
Severity: Critical
Advisory: CVE-2026-24061
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-01-21
Source: https://osv.dev/vulnerability/CVE-2026-24061
Type: osv

## Details
telnetd in GNU Inetutils through 2.7 allows remote authentication bypass via a "-f root" value for the USER environment variable.

## References
- https://www.cisa.gov/known-exploited-vulnerabilities-catalog?field_cve=CVE-2026-24061
- https://www.gnu.org/software/inetutils/
- https://www.vicarius.io/vsociety/posts/cve-2026-24061-mitigation-script-remote-authentication-bypass-in-gnu-inetutils-package
- https://lists.debian.org/debian-lts-announce/2026/01/msg00025.html
- https://www.openwall.com/lists/oss-security/2026/01/20/2#:~:text=root@...a%3A~%20USER='
- https://lists.gnu.org/archive/html/bug-inetutils/2026-01/msg00004.html
- https://www.vicarius.io/vsociety/posts/cve-2026-24061-detection-script-remote-authentication-bypass-in-gnu-inetutils-package
- https://codeberg.org/inetutils/inetutils/commit/ccba9f748aa8d50a38d7748e2e60362edd6a32cc
- https://codeberg.org/inetutils/inetutils/commit/fd702c02497b2f398e739e3119bed0b23dd7aa7b
- http://www.openwall.com/lists/oss-security/2026/01/22/1
- https://www.openwall.com/lists/oss-security/2026/01/20/8
- https://www.openwall.com/lists/oss-security/2026/01/20/2
- https://www.labs.greynoise.io/grimoire/2026-01-22-f-around-and-find-out-18-hours-of-unsolicited-houseguests/index.html
