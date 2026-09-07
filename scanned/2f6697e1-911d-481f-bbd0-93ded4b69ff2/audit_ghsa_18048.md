# [M] slab allows out-of-bounds access in `get_disjoint_mut` due to incorrect bounds check

## Summary
Severity: Medium
Advisory: GHSA-qx2v-8332-m4fv
CVE: CVE-2025-55159
CWE: CWE-119
Ecosystem: crates.io
CVSS: CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-08-11
Source: https://github.com/advisories/GHSA-qx2v-8332-m4fv
Type: github-advisory

## Affected
- crates.io: `slab` — affected >=0.4.10 <0.4.11

## Details
### Impact

The `get_disjoint_mut` method in slab v0.4.10 incorrectly checked if indices were within the slab's capacity instead of its length, allowing access to uninitialized memory. This could lead to undefined behavior or potential crashes.

### Patches

This has been fixed in slab v0.4.11.

### Workarounds

Avoid using `get_disjoint_mut` with indices that might be beyond the slab's actual length, or upgrade to v0.4.11 or later.

### References

- [https://github.com/tokio-rs/slab/pull/152](https://github.com/tokio-rs/slab/pull/152)

## References
- https://github.com/tokio-rs/slab/security/advisories/GHSA-qx2v-8332-m4fv
- https://nvd.nist.gov/vuln/detail/CVE-2025-55159
- https://github.com/tokio-rs/slab/pull/152
- https://github.com/tokio-rs/slab/commit/2d65c514bc964b192bab212ddf3c1fcea4ae96b8
- https://github.com/tokio-rs/slab
- https://rustsec.org/advisories/RUSTSEC-2025-0047.html
