# [M] OHttpVersionChunkDraft: Missing Final-Chunk Enforcement Leads to Undetected Stream Truncation

## Summary
Severity: Medium
Advisory: GHSA-r6fj-869h-4f6q
CVE: CVE-2026-48480
CWE: CWE-325
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N/E:U (CVSS_V4)
Published: 2026-06-23
Source: https://github.com/advisories/GHSA-r6fj-869h-4f6q
Type: github-advisory

## Affected
- Maven: `io.netty.incubator:netty-incubator-codec-ohttp` — affected >=0 <0.0.22.Final

## Details
The codec-ohttp implementation of draft-ietf-ohai-chunked-ohttp does not verify that a cryptographically-signed final chunk was received before the outer HTTP body terminates. An on-path adversary (the OHTTP relay itself, or any MITM on the relay↔gateway or relay↔client transport) can forward a prefix of a legitimate chunked-OHTTP message—cut at a non-final chunk boundary—and close the outer body cleanly, producing no decryption error and no exception in the receiving application.

## References
- https://github.com/netty/netty-incubator-codec-ohttp/security/advisories/GHSA-r6fj-869h-4f6q
- https://nvd.nist.gov/vuln/detail/CVE-2026-48480
- https://github.com/netty/netty-incubator-codec-ohttp/commit/28f977f293591a4e837bd59ceb441f9f70349915
- https://github.com/netty/netty-incubator-codec-ohttp
