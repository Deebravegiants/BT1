# [H] S3 storage write is not aborted on errors leading to unbounded memory usage

## Summary
Severity: High
Advisory: GHSA-m6m5-pp4g-fcc8
CWE: CWE-772
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-10-06
Source: https://github.com/advisories/GHSA-m6m5-pp4g-fcc8
Type: github-advisory

## Affected
- Go: `github.com/foxcpp/maddy` — affected >=0 <0.5.1

## Details
### Impact

Anyone using storage.blob.s3 introduced in 0.5.0 with storage.imapsql.
```
storage.imapsql local_mailboxes {
  ...
  msg_store s3 {
    ...
  }
}
```

### Patches

The relevant commit is pushed to master and will be included in the 0.5.1 release.

No special handling of the issue has been done due to the small amount of affected users.

### Workarounds

None.

### References

* Original report: https://github.com/foxcpp/maddy/issues/395
* Fix: https://github.com/foxcpp/maddy/commit/07c8495ee4394fabbf5aac4df8aebeafb2fb29d8

## References
- https://github.com/foxcpp/maddy/security/advisories/GHSA-m6m5-pp4g-fcc8
- https://github.com/foxcpp/maddy
