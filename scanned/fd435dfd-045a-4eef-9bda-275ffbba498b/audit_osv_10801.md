# [H] CVE-2017-2808

## Summary
Severity: High
Advisory: CVE-2017-2808
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-09-05
Source: https://osv.dev/vulnerability/CVE-2017-2808
Type: osv

## Details
An exploitable use-after-free vulnerability exists in the account parsing component of the Ledger-CLI 3.1.1. A specially crafted ledger file can cause a use-after-free vulnerability resulting in arbitrary code execution. An attacker can convince a user to load a journal file to trigger this vulnerability.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-07/msg00031.html
- http://lists.opensuse.org/opensuse-security-announce/2019-08/msg00029.html
- http://www.securityfocus.com/bid/100546
- https://security.gentoo.org/glsa/202004-05
- https://www.talosintelligence.com/vulnerability_reports/TALOS-2017-0304
