# [H] Denial of service in quinn-proto when using `Endpoint::retry()`

## Summary
Severity: High
Advisory: GHSA-vr26-jcq5-fjj8
CVE: CVE-2024-45311
CWE: CWE-670
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-09-03
Source: https://github.com/advisories/GHSA-vr26-jcq5-fjj8
Type: github-advisory

## Affected
- crates.io: `quinn-proto` — affected >=0.11.0 <0.11.7

## Details
### Summary

As of quinn-proto 0.11, it is possible for a server to `accept()`, `retry()`, `refuse()`, or `ignore()` an `Incoming` connection. However, calling `retry()` on an unvalidated connection exposes the server to a likely panic in the following situations:

- Calling `refuse` or `ignore` on the resulting validated connection, if a duplicate initial packet is received
  - This issue can go undetected until a server's `refuse()`/`ignore()` code path is exercised, such as to stop a denial of service attack.
- Accepting when the initial packet for the resulting validated connection fails to decrypt or exhausts connection IDs, if a similar initial packet that successfully decrypts and doesn't exhaust connection IDs is received.
  - This issue can go undetected if clients are well-behaved.

The former situation was observed in a real application, while the latter is only theoretical.

### Details

Location of panic: https://github.com/quinn-rs/quinn/blob/bb02a12a8435a7732a1d762783eeacbb7e50418e/quinn-proto/src/endpoint.rs#L213

### Impact
Denial of service for internet-facing server

## References
- https://github.com/quinn-rs/quinn/security/advisories/GHSA-vr26-jcq5-fjj8
- https://nvd.nist.gov/vuln/detail/CVE-2024-45311
- https://github.com/quinn-rs/quinn/commit/e01609ccd8738bd438d86fa7185a0f85598cb58f
- https://github.com/quinn-rs/quinn
- https://github.com/quinn-rs/quinn/blob/bb02a12a8435a7732a1d762783eeacbb7e50418e/quinn-proto/src/endpoint.rs#L213
- https://rustsec.org/advisories/RUSTSEC-2024-0373.html
