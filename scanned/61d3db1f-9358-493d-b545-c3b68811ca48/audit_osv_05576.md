# [H] BIT-golang-2021-33194

## Summary
Severity: High
Advisory: BIT-golang-2021-33194
Aliases: CVE-2021-33194, GHSA-83g2-8m93-v3w7, GO-2021-0238
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-golang-2021-33194
Type: osv

## Affected
- Bitnami: `golang` — affected >=1.16.0 <1.16.4

## Details
golang.org/x/net before v0.0.0-20210520170846-37e1c6afe023 allows attackers to cause a denial of service (infinite loop) via crafted ParseFragment input.

## References
- https://github.com/golang/net/commit/37e1c6afe02340126705deced573a85ab75209d7
- https://groups.google.com/g/golang-announce/c/wPunbCPkWUg
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/4CHKSFMHZVOBCZSSVRE3UEYNKARTBMTM/
