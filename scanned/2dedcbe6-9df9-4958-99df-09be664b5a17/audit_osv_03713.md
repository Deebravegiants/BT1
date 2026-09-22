# [M] ALPINE-CVE-2026-42767

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-42767
Ecosystem: Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-06-09
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-42767
Type: osv

## Affected
- Alpine:v3.22: `openssl` — affected >=3.0.0 <3.5.7-r0
- Alpine:v3.23: `openssl` — affected >=3.0.0 <3.5.7-r0
- Alpine:v3.24: `openssl` — affected >=3.0.0 <3.5.7-r0

## Details
Issue summary: An attacker-controlled CMP (Certificate Management Protocol)
server could trigger a NULL pointer dereference in a CMP client application.

Impact summary: A NULL pointer dereference causes a crash of the
application and a Denial of Service.

An attacker controlling a CMP server (or acting as a man-in-the-middle) could
craft a CMP response containing a CRMF (Certificate Request Message Format)
CertRepMessage with an EncryptedValue structure where the symmAlg field
has an algorithm OID but no parameters field. When the OpenSSL CMP client
processes this response, the NULL dereference occurs, causing a crash of
the CMP client.

Applications that process untrusted CMP/CRMF messages may be affected.

The FIPS modules in 4.0, 3.6, 3.5, 3.4, and 3.0 are not affected by this
issue, as the affected code is outside the OpenSSL FIPS module boundary.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-42767
