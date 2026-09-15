# [M] Dependency-Track allows enumeration of managed users via /api/v1/user/login endpoint

## Summary
Severity: Medium
Advisory: CVE-2024-54002
Aliases: GHSA-9w3m-hm36-w32w
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2024-12-04
Source: https://osv.dev/vulnerability/CVE-2024-54002
Type: osv

## Details
Dependency-Track is a Component Analysis platform that allows organizations to identify and reduce risk in the software supply chain. Performing a login request against the /api/v1/user/login endpoint with a username that exist in the system takes significantly longer than performing the same action with a username that is not known by the system. The observable difference in request duration can be leveraged by actors to enumerate valid names of managed users. LDAP and OpenID Connect users are not affected. The issue has been fixed in Dependency-Track 4.12.2.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/54xxx/CVE-2024-54002.json
- https://github.com/DependencyTrack/dependency-track/security/advisories/GHSA-9w3m-hm36-w32w
- https://nvd.nist.gov/vuln/detail/CVE-2024-54002
