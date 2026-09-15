# [H] CVE-2024-48990

## Summary
Severity: High
Advisory: CVE-2024-48990
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-11-19
Source: https://osv.dev/vulnerability/CVE-2024-48990
Type: osv

## Details
Qualys discovered that needrestart, before version 3.8, allows local attackers to execute arbitrary code as root by tricking needrestart into running the Python interpreter with an attacker-controlled PYTHONPATH environment variable.

## References
- http://seclists.org/fulldisclosure/2024/Nov/17
- https://lists.debian.org/debian-lts-announce/2024/11/msg00014.html
- https://www.openwall.com/lists/oss-security/2024/11/19/1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/48xxx/CVE-2024-48990.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-48990
- https://www.qualys.com/2024/11/19/needrestart/needrestart.txt
- https://www.cve.org/CVERecord?id=CVE-2024-48990
- https://github.com/liske/needrestart/commit/fcc9a4401392231bef4ef5ed026a0d7a275149ab
- https://github.com/liske/needrestart
