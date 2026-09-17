# [M] odoh-rs's Invalid Slice Split Results in Server Panic

## Summary
Severity: Medium
Advisory: GHSA-gpcv-p28p-fv2p
CVE: CVE-2023-3766
CWE: CWE-120
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-08-03
Source: https://github.com/advisories/GHSA-gpcv-p28p-fv2p
Type: github-advisory

## Affected
- crates.io: `odoh-rs` — affected >=0 <1.0.2

## Details
A vulnerability was discovered in the odoh-rs rust crate that stems from faulty logic during the parsing of encrypted queries. This issue specifically occurs when processing encrypted query data received from remote clients.

### Impact
An attacker with knowledge of this vulnerability could craft and send specially designed encrypted queries to targeted ODOH servers running with odoh-rs. Upon successful exploitation, the server will crash abruptly, disrupting its normal operation and rendering the service temporarily unavailable.

### Patches
Users are encouraged to update their odoh-rs's rust crate to v1.0.2.

## References
- https://github.com/cloudflare/odoh-rs/security/advisories/GHSA-gpcv-p28p-fv2p
- https://nvd.nist.gov/vuln/detail/CVE-2023-3766
- https://github.com/cloudflare/odoh-rs/pull/28
- https://github.com/cloudflare/odoh-rs/commit/c1bc4ed71dcc9842b7dc1ea26f278f105074bbaa
- https://github.com/cloudflare/odoh-rs
- https://rustsec.org/advisories/RUSTSEC-2023-0095.html
