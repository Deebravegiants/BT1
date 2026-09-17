# [H] netty-incubator-codec-ohttp: BinaryHttpParser should enforce limits for variable lengths fields

## Summary
Severity: High
Advisory: GHSA-hmq9-67w8-j5pw
CVE: CVE-2026-61827
CWE: CWE-400, CWE-770
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-08-20
Source: https://github.com/advisories/GHSA-hmq9-67w8-j5pw
Type: github-advisory

## Affected
- Maven: `io.netty.incubator:netty-incubator-codec-bhttp` — affected >=0 <0.0.23.Final

## Details
We don't enforce any limits for the encoded variable lengths that are used for fields. As the remote peer controls these it's easy for the remote peer to have us buffer data forever and so ultimately OOM.

## References
- https://github.com/netty/netty-incubator-codec-ohttp/security/advisories/GHSA-hmq9-67w8-j5pw
- https://github.com/netty/netty-incubator-codec-ohttp
- https://github.com/netty/netty-incubator-codec-ohttp/releases/tag/netty-incubator-codec-parent-ohttp-0.0.23.Final
