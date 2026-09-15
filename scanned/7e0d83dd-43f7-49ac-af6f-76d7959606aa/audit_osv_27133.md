# [H] CVE-2024-11003

## Summary
Severity: High
Advisory: CVE-2024-11003
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-11-19
Source: https://osv.dev/vulnerability/CVE-2024-11003
Type: osv

## Details
Qualys discovered that needrestart, before version 3.8, passes unsanitized data to a library (Modules::ScanDeps) which expects safe input. This could allow a local attacker to execute arbitrary shell commands. Please see the related CVE-2024-10224 in Modules::ScanDeps.

## References
- http://seclists.org/fulldisclosure/2024/Nov/17
- https://lists.debian.org/debian-lts-announce/2024/11/msg00014.html
- https://www.openwall.com/lists/oss-security/2024/11/19/1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/11xxx/CVE-2024-11003.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-11003
- https://www.qualys.com/2024/11/19/needrestart/needrestart.txt
- https://www.cve.org/CVERecord?id=CVE-2024-10224
- https://www.cve.org/CVERecord?id=CVE-2024-11003
- https://github.com/liske/needrestart/commit/0f80a348883f72279a859ee655f58da34babefb0
- https://github.com/liske/needrestart
