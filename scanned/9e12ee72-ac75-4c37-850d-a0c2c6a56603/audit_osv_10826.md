# [H] CVE-2017-2919

## Summary
Severity: High
Advisory: CVE-2017-2919
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-11-20
Source: https://osv.dev/vulnerability/CVE-2017-2919
Type: osv

## Details
An exploitable stack based buffer overflow vulnerability exists in the xls_getfcell function of libxls 1.3.4. A specially crafted XLS file can cause a memory corruption resulting in remote code execution. An attacker can send malicious XLS file to trigger this vulnerability

## References
- https://security.gentoo.org/glsa/202003-64
- https://www.debian.org/security/2018/dsa-4173
- https://www.talosintelligence.com/vulnerability_reports/TALOS-2017-0426
