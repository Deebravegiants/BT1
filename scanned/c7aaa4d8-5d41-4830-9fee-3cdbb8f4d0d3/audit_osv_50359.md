# [H] CVE-2020-13584

## Summary
Severity: High
Advisory: CVE-2020-13584
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2020-12-03
Source: https://osv.dev/vulnerability/CVE-2020-13584
Type: osv

## Details
An exploitable use-after-free vulnerability exists in WebKitGTK browser version 2.30.1 x64. A specially crafted HTML web page can cause a use-after-free condition, resulting in a remote code execution. The victim needs to visit a malicious web site to trigger this vulnerability.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/BY2OBQZFMEFZOSWXPXHPEHOJXXILEEX2/
- https://security.gentoo.org/glsa/202012-10
- https://talosintelligence.com/vulnerability_reports/TALOS-2020-1195
