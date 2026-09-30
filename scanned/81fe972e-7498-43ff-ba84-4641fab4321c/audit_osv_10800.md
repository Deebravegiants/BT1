# [H] CVE-2017-2807

## Summary
Severity: High
Advisory: CVE-2017-2807
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-09-05
Source: https://osv.dev/vulnerability/CVE-2017-2807
Type: osv

## Details
An exploitable buffer overflow vulnerability exists in the tag parsing functionality of Ledger-CLI 3.1.1. A specially crafted journal file can cause an integer underflow resulting in code execution. An attacker can construct a malicious journal file to trigger this vulnerability.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-07/msg00031.html
- http://lists.opensuse.org/opensuse-security-announce/2019-08/msg00029.html
- http://www.securityfocus.com/bid/100543
- https://security.gentoo.org/glsa/202004-05
- https://www.talosintelligence.com/vulnerability_reports/TALOS-2017-0303
