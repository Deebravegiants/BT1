# [C] ALPINE-CVE-2021-43527

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2021-43527
Ecosystem: Alpine:v3.12, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-12-08
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-43527
Type: osv

## Affected
- Alpine:v3.12: `nss` — affected >=0 <3.60-r2
- Alpine:v3.19: `nss` — affected >=0 <3.73-r0
- Alpine:v3.20: `nss` — affected >=0 <3.73-r0
- Alpine:v3.21: `nss` — affected >=0 <3.73-r0
- Alpine:v3.22: `nss` — affected >=0 <3.73-r0
- Alpine:v3.23: `nss` — affected >=0 <3.73-r0
- Alpine:v3.24: `nss` — affected >=0 <3.73-r0

## Details
NSS (Network Security Services) versions prior to 3.73 or 3.68.1 ESR are vulnerable to a heap overflow when handling DER-encoded DSA or RSA-PSS signatures. Applications using NSS for handling signatures encoded within CMS, S/MIME, PKCS \#7, or PKCS \#12 are likely to be impacted. Applications using NSS for certificate validation or other TLS, X.509, OCSP or CRL functionality may be impacted, depending on how they configure NSS. *Note: This vulnerability does NOT impact Mozilla Firefox.* However, email clients and PDF viewers that use NSS for signature verification, such as Thunderbird, LibreOffice, Evolution and Evince are believed to be impacted. This vulnerability affects NSS < 3.73 and NSS < 3.68.1.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-43527
