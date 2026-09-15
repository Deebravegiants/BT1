# [H] CVE-2020-13543

## Summary
Severity: High
Advisory: CVE-2020-13543
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2020-12-03
Source: https://osv.dev/vulnerability/CVE-2020-13543
Type: osv

## Details
A code execution vulnerability exists in the WebSocket functionality of Webkit WebKitGTK 2.30.0. A specially crafted web page can trigger a use-after-free vulnerability which can lead to remote code execution. An attacker can get a user to visit a webpage to trigger this vulnerability.

## References
- https://security.gentoo.org/glsa/202012-10
- https://www.oracle.com/security-alerts/cpuapr2022.html
- https://talosintelligence.com/vulnerability_reports/TALOS-2020-1155
