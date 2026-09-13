# [H] Denial of Service issue in quinn-proto

## Summary
Severity: High
Advisory: GHSA-q8wc-j5m9-27w3
CVE: CVE-2023-42805
CWE: CWE-20
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-09-21
Source: https://github.com/advisories/GHSA-q8wc-j5m9-27w3
Type: github-advisory

## Affected
- crates.io: `quinn-proto` — affected >=0 <0.9.5

## Details
### Impact

Receiving unknown QUIC frames in a QUIC packet could result in a panic.

### Patches

The problem has been fixed in 0.9.5 and 0.10.5 maintenance releases.

### References

Fixed in https://github.com/quinn-rs/quinn/pull/1667, backported in https://github.com/quinn-rs/quinn/pull/1668 and https://github.com/quinn-rs/quinn/pull/1669.

## References
- https://github.com/quinn-rs/quinn/security/advisories/GHSA-q8wc-j5m9-27w3
- https://nvd.nist.gov/vuln/detail/CVE-2023-42805
- https://github.com/quinn-rs/quinn/pull/1667
- https://github.com/quinn-rs/quinn/pull/1668
- https://github.com/quinn-rs/quinn/pull/1669
- https://github.com/quinn-rs/quinn
- https://rustsec.org/advisories/RUSTSEC-2023-0063.html
