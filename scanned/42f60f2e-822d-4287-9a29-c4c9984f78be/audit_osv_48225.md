# [H] CVE-2017-2924

## Summary
Severity: High
Advisory: CVE-2017-2924
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-04-24
Source: https://osv.dev/vulnerability/CVE-2017-2924
Type: osv

## Details
An exploitable heap-based buffer overflow vulnerability exists in the read_legacy_biff function of FreeXL 1.0.3. A specially crafted XLS file can cause a memory corruption resulting in remote code execution. An attacker can send malicious XLS file to trigger this vulnerability.

## References
- http://www.securityfocus.com/bid/100799
- https://www.debian.org/security/2017/dsa-3976
- https://www.talosintelligence.com/vulnerability_reports/TALOS-2017-0431
