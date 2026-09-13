# [M] ALPINE-CVE-2026-63074

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-63074
Ecosystem: Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-25
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-63074
Type: osv

## Affected
- Alpine:v3.22: `openssl` — affected >=0 <3.5.8-r0
- Alpine:v3.23: `openssl` — affected >=0 <3.5.8-r0
- Alpine:v3.24: `openssl` — affected >=0 <3.5.8-r0

## Details
Issue summary: The OpenSSL Certificate Management Protocol (CMP) caches
additional certificates (extraCerts) sent in a CMP message, but never expunges
them (for instance if they are invalid).  If a server reuses an OSSL_CMP_CTX
frequently, this cache of extraCerts may grow unboundedly, and a malicious
client may flood a CMP server with requests driving this growth.

Impact summary: Users utilizing a CMP server that reuses a single OSSL_CMP_CTX
for the lifetime of a server process may observe unbounded memory growth in the
event a malicious client repeatedly sends requests containing unique extra
certificates, which may lead to OOM conditions.

CWE: CWE-770: Allocation of Resources Without Limits or Throttling

Description: If a remote user sends CMP messages to a server with a list of
extraCerts and the message is rejected, the extraCerts from the message remains
in the server contexts untrusted certificate stack.  This exposes servers with
long lived ctx objects to Denial of Service attacks in which an attacker sends
messages intending to be rejected with a large list of additional certificates
repeatedly, forcing the server to store them indefinitely.
   
The issue was fixed by removing the added extra certs if the message is
rejected, using the same method as when the context is configured to not do
caching at all.

FIPS impact: no
As the CMP code lives outside the FIPS module boundary, no FIPS
modules are affected by this CVE.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-63074
