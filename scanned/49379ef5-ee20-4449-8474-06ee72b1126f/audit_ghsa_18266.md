# [M] FS2 half-shutdown of socket during TLS handshake may result in spin loop on opposite side

## Summary
Severity: Medium
Advisory: GHSA-rrw2-px9j-qffj
CVE: CVE-2025-58369
CWE: CWE-400
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2025-09-05
Source: https://github.com/advisories/GHSA-rrw2-px9j-qffj
Type: github-advisory

## Affected
- Maven: `co.fs2:fs2-io_2.12` — affected >=3.0.0-M1 <3.12.2
- Maven: `co.fs2:fs2-io_2.12` — affected >=3.13.0-M1 <3.13.0-M7
- Maven: `co.fs2:fs2-io_2.13` — affected >=3.0.0-M1 <3.12.2
- Maven: `co.fs2:fs2-io_2.13` — affected >=3.13.0-M1 <3.13.0-M7
- Maven: `co.fs2:fs2-io_3` — affected >=3.0.0-M1 <3.12.2
- Maven: `co.fs2:fs2-io_3` — affected >=3.13.0-M1 <3.13.0-M7
- Maven: `co.fs2:fs2-io_0.26` — affected >=0
- Maven: `co.fs2:fs2-io_0.27` — affected >=0
- Maven: `co.fs2:fs2-io_2.11` — affected >=0
- Maven: `co.fs2:fs2-io_2.12.0-M4` — affected >=0
- Maven: `co.fs2:fs2-io_2.12.0-RC1` — affected >=0
- Maven: `co.fs2:fs2-io_2.12.0-M5` — affected >=0
- Maven: `co.fs2:fs2-io_2.12.0-RC2` — affected >=0
- Maven: `co.fs2:fs2-io_2.13.0-M5` — affected >=0
- Maven: `co.fs2:fs2-io_2.12` — affected >=0 <2.5.13
- Maven: `co.fs2:fs2-io_2.13` — affected >=0 <2.5.13
- Maven: `co.fs2:fs2-io_3` — affected >=0 <2.5.13

## Details
### Impact
When establishing a TLS session using `fs2-io` on the JVM using the `fs2.io.net.tls` package, if one side of the connection shuts down write while the peer side is awaiting more data to progress the TLS handshake, the peer side will spin loop on the socket read, fully utilizing a CPU. This CPU is consumed until the overall connection is closed.

This could be used as a denial of service attack on an fs2-io powered server -- for example, by opening many connections and putting them in a half-shutdown state.

Note: this issue impacts ember backed http4s servers with HTTPS as a result of ember using fs2's TLS support.

### Patches
Fixed in fs2 3.12.2 and 3.13.0-M7.

### Workarounds
No workarounds.

### For more information

If you have any questions or comments about this advisory:

[Open an issue.](https://github.com/typelevel/fs2/issues/new/choose)
Contact the [Typelevel Security Team](https://github.com/typelevel/.github/blob/main/SECURITY.md).

## References
- https://github.com/typelevel/fs2/security/advisories/GHSA-rrw2-px9j-qffj
- https://nvd.nist.gov/vuln/detail/CVE-2025-58369
- https://github.com/typelevel/fs2/issues/3590
- https://github.com/typelevel/fs2/pull/3624
- https://github.com/typelevel/fs2/commit/46e2dc3abf994dcf3d0b804b2ddb3c10c04d4976
- https://github.com/typelevel/fs2/commit/5c6c4c6c1ef330f7e6b53661ecc63d5f5ba8885c
- https://github.com/typelevel/fs2/commit/edf0c4f2e660360d1c1a8c5377ce32294de89238
- https://github.com/typelevel/fs2
- https://github.com/typelevel/fs2/releases/tag/v3.12.2
- https://github.com/typelevel/fs2/releases/tag/v3.13.0-M7
