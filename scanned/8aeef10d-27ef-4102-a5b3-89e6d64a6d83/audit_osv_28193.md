# [M] JumpServer Direct Object Reference (IDOR) Vulnerability in File Manager Bulk Transfer Functionality

## Summary
Severity: Medium
Advisory: CVE-2024-29024
Aliases: GHSA-8wqm-rfc7-q27q
CVSS: 4.6 (CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:U/C:L/I:L/A:L)
Published: 2024-03-29
Source: https://osv.dev/vulnerability/CVE-2024-29024
Type: osv

## Details
JumpServer is an open source bastion host and an operation and maintenance security audit system.
An authenticated user can exploit the Insecure Direct Object Reference (IDOR) vulnerability in the file manager's bulk transfer by manipulating job IDs to upload malicious files,  potentially compromising the integrity and security of the system. This vulnerability is fixed in v3.10.6.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/29xxx/CVE-2024-29024.json
- https://github.com/jumpserver/jumpserver/security/advisories/GHSA-8wqm-rfc7-q27q
- https://nvd.nist.gov/vuln/detail/CVE-2024-29024
