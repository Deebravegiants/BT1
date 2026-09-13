# [H] CVE-2017-7524

## Summary
Severity: High
Advisory: CVE-2017-7524
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2017-06-27
Source: https://osv.dev/vulnerability/CVE-2017-7524
Type: osv

## Details
tpm2-tools versions before 1.1.1 are vulnerable to a password leak due to transmitting password in plaintext from client to server when generating HMAC.

## References
- https://github.com/01org/tpm2.0-tools/commit/c5d72beaab1cbbbe68271f4bc4b6670d69985157
