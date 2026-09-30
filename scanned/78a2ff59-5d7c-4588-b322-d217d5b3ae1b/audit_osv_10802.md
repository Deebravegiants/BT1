# [H] CVE-2017-2816

## Summary
Severity: High
Advisory: CVE-2017-2816
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-09-13
Source: https://osv.dev/vulnerability/CVE-2017-2816
Type: osv

## Details
An exploitable buffer overflow vulnerability exists in the tag parsing functionality of LibOFX 0.9.11. A specially crafted OFX file can cause a write out of bounds resulting in a buffer overflow on the stack. An attacker can construct a malicious OFX file to trigger this vulnerability.

## References
- http://www.securityfocus.com/bid/100828
- https://lists.debian.org/debian-lts-announce/2017/11/msg00038.html
- https://security.gentoo.org/glsa/201908-26
- https://www.talosintelligence.com/vulnerability_reports/TALOS-2017-0317
