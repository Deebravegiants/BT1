# [H] users may append `root` to group listings

## Summary
Severity: High
Advisory: GHSA-m65q-v92h-cm7q
CVE: CVE-2025-5791
CWE: CWE-266
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2025-06-05
Source: https://github.com/advisories/GHSA-m65q-v92h-cm7q
Type: github-advisory

## Affected
- crates.io: `users` — affected >=0.8.0

## Details
Affected versions append `root` to group listings, unless the correct listing has exactly 1024 groups.

This affects both:

- The supplementary groups of a user
- The group access list of the current process

If the caller uses this information for access control, this may lead to privilege escalation.

This crate is not currently maintained, so a patched version is not available.

Versions older than 0.8.0 do not contain the affected functions, so downgrading to them is a workaround.

## Recommended alternatives
- [`uzers`](https://crates.io/crates/uzers) (an actively maintained fork of the `users` crate)
- [`sysinfo`](https://crates.io/crates/sysinfo)

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-5791
- https://github.com/ogham/rust-users/issues/44
- https://access.redhat.com/security/cve/CVE-2025-5791
- https://bugzilla.redhat.com/show_bug.cgi?id=2370001
- https://github.com/ogham/rust-users
- https://rustsec.org/advisories/RUSTSEC-2025-0040.html
