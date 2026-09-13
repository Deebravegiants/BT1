# [H] CVE-2019-5060

## Summary
Severity: High
Advisory: CVE-2019-5060
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-07-31
Source: https://osv.dev/vulnerability/CVE-2019-5060
Type: osv

## Details
An exploitable code execution vulnerability exists in the XPM image rendering function of SDL2_image 2.0.4. A specially crafted XPM image can cause an integer overflow in the colorhash function, allocating too small of a buffer. This buffer can then be written out of bounds, resulting in a heap overflow, ultimately ending in code execution. An attacker can display a specially crafted image to trigger this vulnerability.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-09/msg00012.html
- http://lists.opensuse.org/opensuse-security-announce/2019-09/msg00014.html
- http://lists.opensuse.org/opensuse-security-announce/2019-09/msg00029.html
- http://lists.opensuse.org/opensuse-security-announce/2019-09/msg00030.html
- https://talosintelligence.com/vulnerability_reports/TALOS-2019-0844
