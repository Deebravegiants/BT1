# [M] jackson-databind: InetSocketAddress deserialization triggers eager DNS resolution (SSRF)

## Summary
Severity: Medium
Advisory: GHSA-hgj6-7826-r7m5
CVE: CVE-2026-54514
CWE: CWE-918
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-06-23
Source: https://github.com/advisories/GHSA-hgj6-7826-r7m5
Type: github-advisory

## Affected
- Maven: `com.fasterxml.jackson.core:jackson-databind` — affected >=2.0.0 <2.18.8
- Maven: `com.fasterxml.jackson.core:jackson-databind` — affected >=2.19.0 <2.21.4
- Maven: `com.fasterxml.jackson.core:jackson-databind` — affected >=3.0.0 <3.1.4
- Maven: `tools.jackson.core:jackson-databind` — affected >=2.19.0 <2.21.4
- Maven: `tools.jackson.core:jackson-databind` — affected >=3.0.0 <3.1.4

## Details
## Summary
`JDKFromStringDeserializer` constructed `InetSocketAddress` with `new InetSocketAddress(host, port)`, which performs eager DNS name resolution for hostname inputs at deserialization time. An application that binds untrusted JSON into a type containing an `InetSocketAddress` field issues an attacker-chosen DNS query during `readValue`, before any application-level validation or connect logic. The fix uses `InetSocketAddress.createUnresolved(host, port)`, deferring DNS to an explicit connect.

## Impact
An attacker controlling JSON deserialized into an `InetSocketAddress`-bearing type can force outbound DNS lookups for attacker-chosen hostnames at deserialization time (SSRF / DNS-based out-of-band interaction / internal-resolver probing), purely from binding.

## Affected / Patched (verified via `git tag --contains` on `1f5a103`)
- 2.18 line: `>= 2.18.0, < 2.18.8` -> fixed in **2.18.8**
- 2.19-2.21 line: `>= 2.19.0, < 2.21.4` -> fixed in **2.21.4**
- 3.x line: `>= 3.0.0, < 3.1.4` -> fixed in **3.1.4**

## Severity / CWE
Maintainer: minor. Reporter: LOW. CWE-918 (SSRF).

## Upstream fix
FasterXML/jackson-databind#5951 ("Improve InetSocketAddress deserialization"). Released 2026-06-04 in 2.18.8 / 2.21.4 / 3.1.4.

## Credits
Omkhar Arasaratnam (@omkhar) - finder.

## References
- https://github.com/FasterXML/jackson-databind/security/advisories/GHSA-hgj6-7826-r7m5
- https://nvd.nist.gov/vuln/detail/CVE-2026-54514
- https://github.com/FasterXML/jackson-databind/pull/5951
- https://github.com/FasterXML/jackson-databind/commit/1f5a1037b1e9e05920e755cb35f198bcd46667e4
- https://github.com/FasterXML/jackson-databind
