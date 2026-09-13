# [H] Issue summary: Parsing CMS AuthEnvelopedData message with maliciously crafted AEAD parameters can...

## Summary
Severity: High
Advisory: JLSEC-2026-256
Ecosystem: Julia
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-04-27
Source: https://osv.dev/vulnerability/JLSEC-2026-256
Type: osv

## Affected
- Julia: `OpenSSL_jll` — affected >=3.5.0+0 <3.5.5+0
- Julia: `Openresty_jll` — affected >=1.27.1+0 <1.29.203+0

## Details
Issue summary: Parsing CMS AuthEnvelopedData or EnvelopedData message with
maliciously crafted AEAD parameters can trigger a stack buffer overflow.

Impact summary: A stack buffer overflow may lead to a crash, causing Denial
of Service, or potentially remote code execution.

When parsing CMS (Auth)EnvelopedData structures that use AEAD ciphers such as
AES-GCM, the IV (Initialization Vector) encoded in the ASN.1 parameters is
copied into a fixed-size stack buffer without verifying that its length fits
the destination. An attacker can supply a crafted CMS message with an
oversized IV, causing a stack-based out-of-bounds write before any
authentication or tag verification occurs.

Applications and services that parse untrusted CMS or PKCS#7 content using
AEAD ciphers (e.g., S/MIME (Auth)EnvelopedData with AES-GCM) are vulnerable.
Because the overflow occurs prior to authentication, no valid key material
is required to trigger it. While exploitability to remote code execution
depends on platform and toolchain mitigations, the stack-based write
primitive represents a severe risk.

The FIPS modules in 3.6, 3.5, 3.4, 3.3 and 3.0 are not affected by this
issue, as the CMS implementation is outside the OpenSSL FIPS module
boundary.

OpenSSL 3.6, 3.5, 3.4, 3.3 and 3.0 are vulnerable to this issue.

OpenSSL 1.1.1 and 1.0.2 are not affected by this issue.

## References
- http://www.openwall.com/lists/oss-security/2026/01/27/10
- http://www.openwall.com/lists/oss-security/2026/02/25/6
- https://access.redhat.com/errata/RHSA-2026:1472
- https://access.redhat.com/errata/RHSA-2026:1473
- https://access.redhat.com/errata/RHSA-2026:1496
- https://access.redhat.com/errata/RHSA-2026:1503
- https://access.redhat.com/errata/RHSA-2026:1519
- https://access.redhat.com/errata/RHSA-2026:1594
- https://access.redhat.com/errata/RHSA-2026:1733
- https://access.redhat.com/errata/RHSA-2026:1736
- https://access.redhat.com/errata/RHSA-2026:2072
- https://access.redhat.com/errata/RHSA-2026:2077
- https://access.redhat.com/errata/RHSA-2026:2485
- https://access.redhat.com/errata/RHSA-2026:2563
- https://access.redhat.com/errata/RHSA-2026:2633
- https://access.redhat.com/errata/RHSA-2026:2659
- https://access.redhat.com/errata/RHSA-2026:2671
- https://access.redhat.com/errata/RHSA-2026:2844
- https://access.redhat.com/errata/RHSA-2026:2974
- https://access.redhat.com/errata/RHSA-2026:2995
