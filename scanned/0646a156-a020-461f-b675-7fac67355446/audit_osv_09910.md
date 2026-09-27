# [H] CVE-2017-12111

## Summary
Severity: High
Advisory: CVE-2017-12111
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-11-20
Source: https://osv.dev/vulnerability/CVE-2017-12111
Type: osv

## Details
An exploitable out-of-bounds vulnerability exists in the xls_addCell function of libxls 1.4. A specially crafted XLS file with a formula record can cause memory corruption resulting in remote code execution. An attacker can send a malicious XLS file to trigger this vulnerability.

## References
- https://security.gentoo.org/glsa/202003-64
- https://www.debian.org/security/2018/dsa-4173
- https://www.talosintelligence.com/vulnerability_reports/TALOS-2017-0463
