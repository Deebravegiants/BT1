# [C] Cross-project cluster migration bypasses project restrictions via cluster notification flag

## Summary
Severity: Critical
Advisory: CVE-2026-62420
Aliases: GHSA-v9wr-9r7q-fh4g
CVSS: 9.9 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-08-12
Source: https://osv.dev/vulnerability/CVE-2026-62420
Type: osv

## Details
An authorization bypass vulnerability in LXD allows an authenticated attacker to bypass target project security restrictions during cross-project instance migrations. When moving an instance cross-project to a different cluster member via POST /1.0/instances/{name} with migration: true, project: <target>, and target: <member>, the destination node skips all project restriction checks because the request arrives as an internal cluster notification. An attacker can exploit this to introduce disallowed instance configurations into a restricted project.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/62xxx/CVE-2026-62420.json
- https://github.com/canonical/lxd/security/advisories/GHSA-v9wr-9r7q-fh4g
- https://nvd.nist.gov/vuln/detail/CVE-2026-62420
- https://github.com/canonical/lxd/pull/18605
- https://github.com/canonical/lxd/pull/18651
- https://github.com/canonical/lxd
