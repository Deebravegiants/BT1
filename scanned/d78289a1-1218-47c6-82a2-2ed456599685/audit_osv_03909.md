# [H] ALPINE-CVE-2026-63076

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-63076
Ecosystem: Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-25
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-63076
Type: osv

## Affected
- Alpine:v3.22: `openssl` — affected >=0 <3.5.8-r0
- Alpine:v3.23: `openssl` — affected >=0 <3.5.8-r0
- Alpine:v3.24: `openssl` — affected >=0 <3.5.8-r0

## Details
Issue summary: OpenSSL CMP password based protection verification only
checks whether the protectionAlg parameter was not NULL and not its
ASN.1 type, before treating it as a PBMParameter. A crafted message can
contain a parameter of a different type, which is then dereferenced as an
invalid pointer.

Impact summary: A remote, unauthenticated attacker can crash an application
acting as a CMP server that accepts PBM-protected messages, or a CMP client
talking to a malicious or intercepted CMP server, resulting in a Denial of
Service.

CWE: CWE-476: NULL Pointer Dereference

Description: When verifying the password-based MAC protection of a CMP
message, OpenSSL library reads the protectionAlg algorithm parameter with
X509_ALGOR_get0(), which returns both the parameter type and its value
pointer. The value is then cast to an ASN1_STRING and treated as the
expected PBMParameter after only checking that pointer is not NULL. The
parameter type returned by X509_ALGOR_get0() was never consulted.

This happens during protection verification, before any MAC is computed, so
no knowledge of the PBM shared secret is required; the only precondition is
that PBM verification is reachable. On the server side this is reached from
OSSL_CMP_SRV_process_request() for any application that stands up a CMP
server accepting PBM-protected messages, and on the client side from CMP
response validation against a malicious or on-path (MITM) server. The
reliable consequence is a denial of service; there is no memory disclosure,
no controlled memory write, and no path to code execution. CMP is a
specialized feature that an application must explicitly enable.

FIPS impact: no
As the CMP code lives outside the FIPS module boundary, no FIPS modules
are affected by this CVE.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-63076
