# [M] SpiceDB exclusions can result in no permission returned when permission expected

## Summary
Severity: Medium
Advisory: GHSA-grjv-gjgr-66g2
CVE: CVE-2024-38361
CWE: CWE-281
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2024-06-20
Source: https://github.com/advisories/GHSA-grjv-gjgr-66g2
Type: github-advisory

## Affected
- Go: `github.com/authzed/spicedb` — affected >=0 <1.33.1

## Details
### Background

Use of an exclusion under an arrow that has multiple resources may resolve to `NO_PERMISSION` when permission is expected.

For example, given this schema:

```zed
definition user {}

definition folder {
  relation member: user
  relation banned: user
  permission view = member - banned
}

definition resource {
  relation folder: folder
  permission view = folder->view
}
```

If the resource exists under *multiple* folders and the user has access to view more than a single folder, SpiceDB may report the user does not have access due to a failure in the exclusion dispatcher to request that *all* the folders in which the user is a member be returned

### Impact

Permission is returned as `NO_PERMISSION` when `PERMISSION` is expected on the `CheckPermission` API.

### Workarounds

None

## References
- https://github.com/authzed/spicedb/security/advisories/GHSA-grjv-gjgr-66g2
- https://nvd.nist.gov/vuln/detail/CVE-2024-38361
- https://github.com/authzed/spicedb/commit/ecef31d2b266fde17eb2c3415e2ec4ceff96fbeb
- https://github.com/authzed/spicedb
