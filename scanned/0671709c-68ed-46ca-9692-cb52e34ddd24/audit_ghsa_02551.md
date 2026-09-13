# [H] Excessive memory usage in tokio-rustls

## Summary
Severity: High
Advisory: GHSA-2jfv-g3fh-xq3v
CVE: CVE-2020-35875
CWE: CWE-400
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-2jfv-g3fh-xq3v
Type: github-advisory

## Affected
- crates.io: `tokio-rustls` — affected >=0.12.0 <0.12.3
- crates.io: `tokio-rustls` — affected >=0.13.0 <0.13.1

## Details
tokio-rustls does not call process_new_packets immediately after read, so the expected termination condition wants_read always returns true. As long as new incoming data arrives faster than it is processed and the reader does not return pending, data will be buffered. This may cause DoS.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-35875
- https://github.com/tokio-rs/tls/pull/14
- https://github.com/tokio-rs/tls
- https://rustsec.org/advisories/RUSTSEC-2020-0019.html
