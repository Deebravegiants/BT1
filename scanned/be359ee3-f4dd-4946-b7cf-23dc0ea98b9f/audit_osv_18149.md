# [M] CVE-2020-24585

## Summary
Severity: Medium
Advisory: CVE-2020-24585
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2020-08-21
Source: https://osv.dev/vulnerability/CVE-2020-24585
Type: osv

## Details
An issue was discovered in the DTLS handshake implementation in wolfSSL before 4.5.0. Clear DTLS application_data messages in epoch 0 do not produce an out-of-order error. Instead, these messages are returned to the application.

## References
- https://github.com/wolfSSL/wolfssl/pull/3219
- https://github.com/wolfSSL/wolfssl/releases/tag/v4.5.0-stable
