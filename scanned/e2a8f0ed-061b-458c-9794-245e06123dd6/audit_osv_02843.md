# [M] ALPINE-CVE-2023-3446

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2023-3446
Ecosystem: Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2023-07-19
Source: https://osv.dev/vulnerability/ALPINE-CVE-2023-3446
Type: osv

## Affected
- Alpine:v3.15: `openssl` — affected >=0 <1.1.1u-r2
- Alpine:v3.16: `openssl` — affected >=0 <1.1.1u-r2
- Alpine:v3.17: `openssl` — affected >=0 <3.0.9-r3
- Alpine:v3.18: `openssl` — affected >=0 <3.1.1-r3
- Alpine:v3.19: `openssl` — affected >=0 <3.1.1-r3
- Alpine:v3.20: `openssl` — affected >=0 <3.1.1-r3
- Alpine:v3.21: `openssl` — affected >=0 <3.1.1-r3
- Alpine:v3.22: `openssl` — affected >=0 <3.1.1-r3
- Alpine:v3.23: `openssl` — affected >=0 <3.1.1-r3
- Alpine:v3.24: `openssl` — affected >=0 <3.1.1-r3
- Alpine:v3.15: `openssl3` — affected >=0 <3.0.9-r2
- Alpine:v3.16: `openssl3` — affected >=0 <3.0.9-r2

## Details
Issue summary: Checking excessively long DH keys or parameters may be very slow.

Impact summary: Applications that use the functions DH_check(), DH_check_ex()
or EVP_PKEY_param_check() to check a DH key or DH parameters may experience long
delays. Where the key or parameters that are being checked have been obtained
from an untrusted source this may lead to a Denial of Service.

The function DH_check() performs various checks on DH parameters. One of those
checks confirms that the modulus ('p' parameter) is not too large. Trying to use
a very large modulus is slow and OpenSSL will not normally use a modulus which
is over 10,000 bits in length.

However the DH_check() function checks numerous aspects of the key or parameters
that have been supplied. Some of those checks use the supplied modulus value
even if it has already been found to be too large.

An application that calls DH_check() and supplies a key or parameters obtained
from an untrusted source could be vulernable to a Denial of Service attack.

The function DH_check() is itself called by a number of other OpenSSL functions.
An application calling any of those other functions may similarly be affected.
The other functions affected by this are DH_check_ex() and
EVP_PKEY_param_check().

Also vulnerable are the OpenSSL dhparam and pkeyparam command line applications
when using the '-check' option.

The OpenSSL SSL/TLS implementation is not affected by this issue.
The OpenSSL 3.0 and 3.1 FIPS providers are not affected by this issue.

## References
- https://security.alpinelinux.org/vuln/CVE-2023-3446
