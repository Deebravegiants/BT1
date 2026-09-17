# [H] CVE-2019-5051

## Summary
Severity: High
Advisory: CVE-2019-5051
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-07-03
Source: https://osv.dev/vulnerability/CVE-2019-5051
Type: osv

## Details
An exploitable heap-based buffer overflow vulnerability exists when loading a PCX file in SDL2_image, version 2.0.4. A missing error handler can lead to a buffer overflow and potential code execution. An attacker can provide a specially crafted image file to trigger this vulnerability.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-09/msg00012.html
- http://lists.opensuse.org/opensuse-security-announce/2019-09/msg00029.html
- https://lists.debian.org/debian-lts-announce/2019/07/msg00026.html
- https://usn.ubuntu.com/4238-1/
- https://talosintelligence.com/vulnerability_reports/TALOS-2019-0820
