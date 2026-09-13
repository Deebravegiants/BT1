# [M] listmonk: Broken Access Control in CSV Import (Unauthorized List Assignment)

## Summary
Severity: Medium
Advisory: CVE-2026-34584
Aliases: GHSA-85j8-5c6w-gcpv
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N)
Published: 2026-04-02
Source: https://osv.dev/vulnerability/CVE-2026-34584
Type: osv

## Details
listmonk is a standalone, self-hosted, newsletter and mailing list manager. From version 4.1.0 to before version 6.1.0, bugs in list permission checks allows users in a multi-user environment to access to lists (which they don't have access to) under different scenarios. This only affects multi-user environments with untrusted users. This issue has been patched in version 6.1.0.

## References
- https://github.com/knadh/listmonk/releases/tag/v6.1.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/34xxx/CVE-2026-34584.json
- https://github.com/knadh/listmonk/security/advisories/GHSA-85j8-5c6w-gcpv
- https://nvd.nist.gov/vuln/detail/CVE-2026-34584
- https://github.com/knadh/listmonk/commit/347f5976759232c36e571cf58b4bfe33c2794f35
