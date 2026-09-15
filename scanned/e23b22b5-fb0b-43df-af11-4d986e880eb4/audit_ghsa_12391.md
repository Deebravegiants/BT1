# [M] Remotely exploitable denial of service in Rosenpass

## Summary
Severity: Medium
Advisory: GHSA-6ggr-cwv4-g7qg
CVE: CVE-2023-53157
CWE: CWE-130
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2023-12-21
Source: https://github.com/advisories/GHSA-6ggr-cwv4-g7qg
Type: github-advisory

## Affected
- crates.io: `rosenpass` — affected >=0 <0.2.1

## Details
Affected versions of this crate did not validate the size of buffers when attempting to decode messages.

This allows an attacker to trigger a panic by sending a UDP datagram with a 1 byte payload over network.

This flaw was corrected by validating the size of the buffers before attempting to decode the message.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-53157
- https://github.com/rosenpass/rosenpass/commit/93439858d1c44294a7b377f775c4fc897a370bb2
- https://github.com/rosenpass/rosenpass
- https://rustsec.org/advisories/RUSTSEC-2023-0077.html
