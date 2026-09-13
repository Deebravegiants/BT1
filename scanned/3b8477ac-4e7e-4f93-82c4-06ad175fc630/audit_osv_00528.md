# [C] ALPINE-CVE-2017-15088

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2017-15088
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-11-23
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-15088
Type: osv

## Affected
- Alpine:v3.10: `krb5` — affected >=0 <1.15.3-r0
- Alpine:v3.11: `krb5` — affected >=0 <1.15.3-r0
- Alpine:v3.12: `krb5` — affected >=0 <1.15.3-r0
- Alpine:v3.13: `krb5` — affected >=0 <1.15.3-r0
- Alpine:v3.14: `krb5` — affected >=0 <1.15.3-r0
- Alpine:v3.15: `krb5` — affected >=0 <1.15.3-r0
- Alpine:v3.16: `krb5` — affected >=0 <1.15.3-r0
- Alpine:v3.17: `krb5` — affected >=0 <1.15.3-r0
- Alpine:v3.18: `krb5` — affected >=0 <1.15.3-r0
- Alpine:v3.19: `krb5` — affected >=0 <1.15.3-r0
- Alpine:v3.20: `krb5` — affected >=0 <1.15.3-r0
- Alpine:v3.21: `krb5` — affected >=0 <1.15.3-r0
- Alpine:v3.22: `krb5` — affected >=0 <1.15.3-r0
- Alpine:v3.23: `krb5` — affected >=0 <1.15.3-r0
- Alpine:v3.24: `krb5` — affected >=0 <1.15.3-r0
- Alpine:v3.7: `krb5` — affected >=0 <1.15.3-r0
- Alpine:v3.8: `krb5` — affected >=0 <1.15.3-r0
- Alpine:v3.9: `krb5` — affected >=0 <1.15.3-r0

## Details
plugins/preauth/pkinit/pkinit_crypto_openssl.c in MIT Kerberos 5 (aka krb5) through 1.15.2 mishandles Distinguished Name (DN) fields, which allows remote attackers to execute arbitrary code or cause a denial of service (buffer overflow and application crash) in situations involving untrusted X.509 data, related to the get_matching_data and X509_NAME_oneline_ex functions. NOTE: this has security relevance only in use cases outside of the MIT Kerberos distribution, e.g., the use of get_matching_data in KDC certauth plugin code that is specific to Red Hat.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-15088
