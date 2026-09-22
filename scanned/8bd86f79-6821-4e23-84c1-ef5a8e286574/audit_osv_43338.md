# [H] RustFS: Object Lock (WORM) protections are treated as absent when bucket metadata cannot be read, allowing retained objects to be deleted

## Summary
Severity: High
Advisory: CVE-2026-73288
Aliases: GHSA-j548-9grx-fh4f
CVSS: 7.5 (CVSS:4.0/AV:N/AC:H/AT:P/PR:L/UI:N/VC:N/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-12
Source: https://osv.dev/vulnerability/CVE-2026-73288
Type: osv

## Details
RustFS is a distributed object storage system built in Rust. Prior to 1.0.0-rc.1, RustFS Object Lock enforcement in crates/ecstore/src/bucket/object_lock/objectlock_sys.rs lets check_object_lock_for_deletion, delete_prefix, and lifecycle and scanner sweeps treat ConfigNotFound, unreadable .metadata.bin data, or unparseable metadata as no lock configuration, allowing objects under COMPLIANCE retention to be deleted or expired. This issue is fixed in version 1.0.0-rc.1.

## References
- https://github.com/rustfs/rustfs/releases/tag/1.0.0-rc.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/73xxx/CVE-2026-73288.json
- https://github.com/rustfs/rustfs/security/advisories/GHSA-j548-9grx-fh4f
- https://nvd.nist.gov/vuln/detail/CVE-2026-73288
- https://github.com/rustfs/rustfs/commit/98d3619613722308498494d412797a52ea8ae64d
- https://github.com/rustfs/rustfs/pull/5648
