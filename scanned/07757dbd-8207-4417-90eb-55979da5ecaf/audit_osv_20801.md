# [C] CVE-2021-37155

## Summary
Severity: Critical
Advisory: CVE-2021-37155
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-07-21
Source: https://osv.dev/vulnerability/CVE-2021-37155
Type: osv

## Details
wolfSSL 4.6.x through 4.7.x before 4.8.0 does not produce a failure outcome when the serial number in an OCSP request differs from the serial number in the OCSP response.

## References
- https://github.com/wolfSSL/wolfssl/releases/tag/v4.8.0-stable
- https://github.com/wolfSSL/wolfssl/pull/3990
