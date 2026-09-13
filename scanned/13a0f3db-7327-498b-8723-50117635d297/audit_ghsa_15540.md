# [M] SpiceDB having multiple caveats on resources of the same type may improperly result in no permission

## Summary
Severity: Medium
Advisory: GHSA-jhg6-6qrx-38mr
CVE: CVE-2024-46989
CWE: CWE-269, CWE-285
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2024-09-18
Source: https://github.com/advisories/GHSA-jhg6-6qrx-38mr
Type: github-advisory

## Affected
- Go: `github.com/authzed/spicedb` — affected >=0 <1.35.3

## Details
## Background

Multiple caveats over the same indirect subject type on the same relation can result in no permission being returned when permission is expected

For example, given this schema:

```
definition user {}

caveat somecaveat(somefield int) {
  somefield == 42
}

definition group {
  relation member: user
}

definition resource {
  relation viewer: group#member with somecaveat
  permission view = folder->view
}
```

If the resource has multiple groups, and each group is caveated, it is possible for the returned permission to be "no permission" when permission is expected.

## Impact
Permission is returned as NO_PERMISSION when PERMISSION is expected on the CheckPermission API.

## Workarounds
Do not use caveats or do not use caveats on an indirect subject type with multiple entries

## References
- https://github.com/authzed/spicedb/security/advisories/GHSA-jhg6-6qrx-38mr
- https://nvd.nist.gov/vuln/detail/CVE-2024-46989
- https://github.com/authzed/spicedb/commit/20855de75812bcbc975efebe7f76abf47c0f3edb
- https://github.com/authzed/spicedb/commit/d4ef8e1dbce1eafaf25847f4c0f09738820f5bf2
- https://github.com/authzed/spicedb
