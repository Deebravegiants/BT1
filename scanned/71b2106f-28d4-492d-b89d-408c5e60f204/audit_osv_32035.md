# [H] CVE-2025-22923

## Summary
Severity: High
Advisory: CVE-2025-22923
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-04-02
Source: https://osv.dev/vulnerability/CVE-2025-22923
Type: osv

## Details
An issue in OS4ED openSIS v8.0 through v9.1 allows attackers to execute a directory traversal and delete files by sending a crafted POST request to /Modules.php?modname=users/Staff.php&removefile.

## References
- https://github.com/esusalla/vulnerability-research/tree/main/CVE-2025-22923
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/22xxx/CVE-2025-22923.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-22923
- https://github.com/OS4ED/openSIS-Classic
