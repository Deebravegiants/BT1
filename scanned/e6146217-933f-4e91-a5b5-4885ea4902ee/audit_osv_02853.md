# [M] ALPINE-CVE-2023-3817

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2023-3817
Ecosystem: Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2023-07-31
Source: https://osv.dev/vulnerability/ALPINE-CVE-2023-3817
Type: osv

## Affected
- Alpine:v3.15: `openssl` — affected >=3.0.0 <1.1.1v-r0
- Alpine:v3.16: `openssl` — affected >=3.0.0 <1.1.1v-r0
- Alpine:v3.17: `openssl` — affected >=3.0.0 <3.0.10-r0
- Alpine:v3.18: `openssl` — affected >=3.0.0 <3.1.2-r0
- Alpine:v3.19: `openssl` — affected >=3.0.0 <3.1.2-r0
- Alpine:v3.20: `openssl` — affected >=3.0.0 <3.1.2-r0
- Alpine:v3.21: `openssl` — affected >=3.0.0 <3.1.2-r0
- Alpine:v3.22: `openssl` — affected >=3.0.0 <3.1.2-r0
- Alpine:v3.23: `openssl` — affected >=3.0.0 <3.1.2-r0
- Alpine:v3.24: `openssl` — affected >=3.0.0 <3.1.2-r0
- Alpine:v3.15: `openssl3` — affected >=0 <3.0.11-r0
- Alpine:v3.16: `openssl3` — affected >=0 <3.0.11-r0

## Details
Issue summary: Checking excessively long DH keys or parameters may be very slow.

Impact summary: Applications that use the functions DH_check(), DH_check_ex()
or EVP_PKEY_param_check() to check a DH key or DH parameters may experience long
delays. Where the key or parameters that are being checked have been obtained
from an untrusted source this may lead to a Denial of Service.

The function DH_check() performs various checks on DH parameters. After fixing
CVE-2023-3446 it was discovered that a large q parameter value can also trigger
an overly long computation during some of these checks. A correct q value,
if present, cannot be larger than the modulus p parameter, thus it is
unnecessary to perform these checks if q is larger than p.

An application that calls DH_check() and supplies a key or parameters obtained
from an untrusted source could be vulnerable to a Denial of Service attack.

The function DH_check() is itself called by a number of other OpenSSL functions.
An application calling any of those other functions may similarly be affected.
The other functions affected by this are DH_check_ex() and
EVP_PKEY_param_check().

Also vulnerable are the OpenSSL dhparam and pkeyparam command line applications
when using the "-check" option.

The OpenSSL SSL/TLS implementation is not affected by this issue.

The OpenSSL 3.0 and 3.1 FIPS providers are not affected by this issue.

## References
- https://security.alpinelinux.org/vuln/CVE-2023-3817
