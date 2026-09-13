# [H] CVE-2024-48992

## Summary
Severity: High
Advisory: CVE-2024-48992
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-11-19
Source: https://osv.dev/vulnerability/CVE-2024-48992
Type: osv

## Details
Qualys discovered that needrestart, before version 3.8, allows local attackers to execute arbitrary code as root by tricking needrestart into running the Ruby interpreter with an attacker-controlled RUBYLIB environment variable.

## References
- http://seclists.org/fulldisclosure/2024/Nov/17
- https://lists.debian.org/debian-lts-announce/2024/11/msg00014.html
- https://www.openwall.com/lists/oss-security/2024/11/19/1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/48xxx/CVE-2024-48992.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-48992
- https://www.qualys.com/2024/11/19/needrestart/needrestart.txt
- https://www.cve.org/CVERecord?id=CVE-2024-48992
- https://github.com/liske/needrestart/commit/b5f25f6ec6e7dd0c5be249e4e45de4ee9ffe594f
- https://github.com/liske/needrestart
