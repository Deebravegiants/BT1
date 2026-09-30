# [M] ALPINE-CVE-2026-42766

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-42766
Ecosystem: Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-06-09
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-42766
Type: osv

## Affected
- Alpine:v3.22: `openssl` — affected >=1.0.2 <3.5.7-r0
- Alpine:v3.23: `openssl` — affected >=1.0.2 <3.5.7-r0
- Alpine:v3.24: `openssl` — affected >=1.0.2 <3.5.7-r0

## Details
Issue summary: A specially crafted password-encrypted CMS message
can trigger a NULL pointer dereference during CMS decryption.

Impact summary: This NULL pointer dereference leads to an application crash
and a Denial of Service.

The CMS PasswordRecipientInfo.keyDerivationAlgorithm field is defined as
OPTIONAL in the ASN.1 specification and may therefore be absent in specially
crafted inputs. During the password-based CMS decryption the OpenSSL
CMS implementation dereferences this field without first checking whether it
was present.

An attacker who supplies such a CMS message to an application performing
password-based CMS decryption can trigger an application crash, leading to
a Denial of Service.

Applications that process password-encrypted CMS messages may be affected.

The FIPS modules in 4.0, 3.6, 3.5, 3.4, and 3.0 are not affected by this
issue, as the affected code is outside the OpenSSL FIPS module boundary.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-42766
