# [M] ALPINE-CVE-2023-5678

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2023-5678
Ecosystem: Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2023-11-06
Source: https://osv.dev/vulnerability/ALPINE-CVE-2023-5678
Type: osv

## Affected
- Alpine:v3.15: `openssl` — affected >=1.0.2 <1.1.1w-r1
- Alpine:v3.16: `openssl` — affected >=1.0.2 <1.1.1w-r1
- Alpine:v3.17: `openssl` — affected >=1.0.2 <3.0.12-r1
- Alpine:v3.18: `openssl` — affected >=1.0.2 <3.1.4-r1
- Alpine:v3.19: `openssl` — affected >=1.0.2 <3.1.4-r1
- Alpine:v3.20: `openssl` — affected >=1.0.2 <3.1.4-r1
- Alpine:v3.21: `openssl` — affected >=1.0.2 <3.1.4-r1
- Alpine:v3.22: `openssl` — affected >=1.0.2 <3.1.4-r1
- Alpine:v3.23: `openssl` — affected >=1.0.2 <3.1.4-r1
- Alpine:v3.24: `openssl` — affected >=1.0.2 <3.1.4-r1

## Details
Issue summary: Generating excessively long X9.42 DH keys or checking
excessively long X9.42 DH keys or parameters may be very slow.

Impact summary: Applications that use the functions DH_generate_key() to
generate an X9.42 DH key may experience long delays.  Likewise, applications
that use DH_check_pub_key(), DH_check_pub_key_ex() or EVP_PKEY_public_check()
to check an X9.42 DH key or X9.42 DH parameters may experience long delays.
Where the key or parameters that are being checked have been obtained from
an untrusted source this may lead to a Denial of Service.

While DH_check() performs all the necessary checks (as of CVE-2023-3817),
DH_check_pub_key() doesn't make any of these checks, and is therefore
vulnerable for excessively large P and Q parameters.

Likewise, while DH_generate_key() performs a check for an excessively large
P, it doesn't check for an excessively large Q.

An application that calls DH_generate_key() or DH_check_pub_key() and
supplies a key or parameters obtained from an untrusted source could be
vulnerable to a Denial of Service attack.

DH_generate_key() and DH_check_pub_key() are also called by a number of
other OpenSSL functions.  An application calling any of those other
functions may similarly be affected.  The other functions affected by this
are DH_check_pub_key_ex(), EVP_PKEY_public_check(), and EVP_PKEY_generate().

Also vulnerable are the OpenSSL pkey command line application when using the
"-pubcheck" option, as well as the OpenSSL genpkey command line application.

The OpenSSL SSL/TLS implementation is not affected by this issue.

The OpenSSL 3.0 and 3.1 FIPS providers are not affected by this issue.

## References
- https://security.alpinelinux.org/vuln/CVE-2023-5678
