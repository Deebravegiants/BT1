# [H] FACTION Allows Authentication Bypass via User Creation

## Summary
Severity: High
Advisory: CVE-2025-27422
Aliases: GHSA-97cv-f342-v2jc
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2025-03-03
Source: https://osv.dev/vulnerability/CVE-2025-27422
Type: osv

## Details
FACTION is a PenTesting Report Generation and Collaboration Framework. Authentication is bypassed when an attacker registers a new user with admin privileges. This is possible at any time without any authorization. The request must follow the validation rules (no missing information, secure password, etc) but there are no other controls stopping them. This vulnerability is fixed in 1.4.3.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/27xxx/CVE-2025-27422.json
- https://github.com/factionsecurity/faction/security/advisories/GHSA-97cv-f342-v2jc
- https://nvd.nist.gov/vuln/detail/CVE-2025-27422
- https://github.com/factionsecurity/faction/commit/0a6848d388d6dba1c81918cce2772b1e805cd3d6
