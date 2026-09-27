# [C] CVE-2025-22927

## Summary
Severity: Critical
Advisory: CVE-2025-22927
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2025-04-03
Source: https://osv.dev/vulnerability/CVE-2025-22927
Type: osv

## Details
An issue in OS4ED openSIS v8.0 through v9.1 allows attackers to execute a directory traversal by sending a crafted POST request to /Modules.php?modname=messaging/Inbox.php&modfunc=save&filename.

## References
- https://github.com/esusalla/vulnerability-research/tree/main/CVE-2025-22927
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/22xxx/CVE-2025-22927.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-22927
- https://github.com/OS4ED/openSIS-Classic
