# [M] ChirpStack SQLite Backend SQL Injection via Device Tag Key in ListDevices Filter

## Summary
Severity: Medium
Advisory: CVE-2026-71282
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-08-05
Source: https://osv.dev/vulnerability/CVE-2026-71282
Type: osv

## Details
ChirpStack's SQLite-backend device tag filtering (chirpstack/src/storage/device.rs, in both get_count and list) interpolates the user-supplied tag KEY directly into a raw SQL fragment via Rust's format! macro , while only the tag VALUE is safely parameter-bound via Diesel's .bind.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/71xxx/CVE-2026-71282.json
- https://github.com/chirpstack/chirpstack
- https://github.com/chirpstack/chirpstack/blob/master/chirpstack/src/storage/device.rs
- https://nvd.nist.gov/vuln/detail/CVE-2026-71282
