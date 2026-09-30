# [H] CVE-2020-12457

## Summary
Severity: High
Advisory: CVE-2020-12457
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-08-21
Source: https://osv.dev/vulnerability/CVE-2020-12457
Type: osv

## Details
An issue was discovered in wolfSSL before 4.5.0. It mishandles the change_cipher_spec (CCS) message processing logic for TLS 1.3. If an attacker sends ChangeCipherSpec messages in a crafted way involving more than one in a row, the server becomes stuck in the ProcessReply() loop, i.e., a denial of service.

## References
- https://github.com/wolfSSL/wolfssl/releases/tag/v4.5.0-stable
- https://github.com/wolfSSL/wolfssl/pull/2927
