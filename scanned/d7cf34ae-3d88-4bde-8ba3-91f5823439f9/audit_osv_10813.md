# [H] CVE-2017-2897

## Summary
Severity: High
Advisory: CVE-2017-2897
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-11-20
Source: https://osv.dev/vulnerability/CVE-2017-2897
Type: osv

## Details
An exploitable out-of-bounds write vulnerability exists in the read_MSAT function of libxls 1.4. A specially crafted XLS file can cause a memory corruption resulting in remote code execution. An attacker can send malicious XLS file to trigger this vulnerability.

## References
- https://security.gentoo.org/glsa/202003-64
- https://www.debian.org/security/2018/dsa-4173
- https://www.talosintelligence.com/vulnerability_reports/TALOS-2017-0404
