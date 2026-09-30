# [C] fs2-io skips mTLS client verification

## Summary
Severity: Critical
Advisory: GHSA-2cpx-6pqp-wf35
CVE: CVE-2022-31183
CWE: CWE-295
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-07-29
Source: https://github.com/advisories/GHSA-2cpx-6pqp-wf35
Type: github-advisory

## Affected
- Maven: `co.fs2:fs2-io` — affected >=3.1.0 <3.2.11
- Maven: `co.fs2:fs2-io_2.12` — affected >=3.1.0 <3.2.11
- Maven: `co.fs2:fs2-io_3` — affected >=3.1.0 <3.2.11
- Maven: `co.fs2:fs2-io_2.13` — affected >=3.1.0 <3.2.11
- Maven: `co.fs2:fs2-io_sjs1_2.13` — affected >=3.1.0 <3.2.11
- Maven: `co.fs2:fs2-io_sjs1_3` — affected >=3.1.0 <3.2.11

## Details
### Impact

When establishing a server-mode `TLSSocket` using `fs2-io` on Node.js, the parameter `requestCert = true` is ignored, peer certificate verification is skipped, and the connection proceeds.

The vulnerability is limited to:
1. `fs2-io` running on Node.js. The JVM TLS implementation is completely independent.
2. `TLSSocket`s in server-mode. Client-mode `TLSSocket`s are implemented via a different API.
3. mTLS as enabled via `requestCert = true` in `TLSParameters`. The default setting is `false` for server-mode `TLSSocket`s.

It was introduced with the initial Node.js implementation of fs2-io in v3.1.0.

### Patches

A patch is released in v3.2.11. The `requestCert = true` parameter is respected and the peer certificate is verified. If verification fails, a `SSLException` is raised.

### Workarounds

If using an unpatched version on Node.js, do not use a server-mode `TLSSocket` with `requestCert = true` to establish a mTLS connection.

### References
- https://github.com/nodejs/node/issues/43994
- https://www.cloudflare.com/learning/access-management/what-is-mutual-tls/

### For more information
If you have any questions or comments about this advisory:
* [Open an issue.](https://github.com/typelevel/fs2/issues/new/choose)
* Contact the [Typelevel Security Team](https://github.com/typelevel/.github/blob/main/SECURITY.md).

## References
- https://github.com/typelevel/fs2/security/advisories/GHSA-2cpx-6pqp-wf35
- https://nvd.nist.gov/vuln/detail/CVE-2022-31183
- https://github.com/nodejs/node/issues/43994
- https://github.com/typelevel/fs2/commit/19ce392e8093d9571387dbd78e159e655a85aeea
- https://github.com/typelevel/fs2/commit/659824395826a314e0a4331535dbf1ef8bef8207
- https://github.com/typelevel/fs2
- https://github.com/typelevel/fs2/releases/tag/v3.2.11
