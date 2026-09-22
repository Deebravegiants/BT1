# [H] Tungstenite allows remote attackers to cause a denial of service

## Summary
Severity: High
Advisory: GHSA-9mcr-873m-xcxp
CVE: CVE-2023-43669
CWE: CWE-400
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-09-21
Source: https://github.com/advisories/GHSA-9mcr-873m-xcxp
Type: github-advisory

## Affected
- crates.io: `tungstenite` — affected >=0 <0.20.1

## Details
The Tungstenite crate through 0.20.0 for Rust allows remote attackers to cause a denial of service (minutes of CPU consumption) via an excessive length of an HTTP header in a client handshake. The length affects both how many times a parse is attempted (e.g., thousands of times) and the average amount of data for each parse attempt (e.g., millions of bytes).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-43669
- https://github.com/snapview/tungstenite-rs/issues/376
- https://github.com/github/advisory-database/pull/2752
- https://github.com/snapview/tungstenite-rs/pull/379
- https://github.com/snapview/tungstenite-rs/commit/8b3ecd3cc0008145ab4bc8d0657c39d09db8c7e2
- https://security-tracker.debian.org/tracker/CVE-2023-43669
- https://rustsec.org/advisories/RUSTSEC-2023-0065.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/TT7SF6CQ5VHAGFLWNXY64NFSW4WIWE7D
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/THK6G6CD4VW6RCROWUV2C4HSINKK3XAK
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/R77EUWPZVP5WSMNXUXUDNHR7G7OI5NGM
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/TT7SF6CQ5VHAGFLWNXY64NFSW4WIWE7D
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/THK6G6CD4VW6RCROWUV2C4HSINKK3XAK
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/R77EUWPZVP5WSMNXUXUDNHR7G7OI5NGM
- https://github.com/snapview/tungstenite-rs
- https://github.com/advisories/GHSA-9mcr-873m-xcxp
- https://cwe.mitre.org/data/definitions/407.html
- https://crates.io/crates/tungstenite/versions
- https://bugzilla.suse.com/show_bug.cgi?id=1215563
- https://bugzilla.redhat.com/show_bug.cgi?id=2240110
