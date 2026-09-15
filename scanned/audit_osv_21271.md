# [M] CVE-2021-41581

## Summary
Severity: Medium
Advisory: CVE-2021-41581
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2021-09-24
Source: https://osv.dev/vulnerability/CVE-2021-41581
Type: osv

## Details
x509_constraints_parse_mailbox in lib/libcrypto/x509/x509_constraints.c in LibreSSL through 3.4.0 has a stack-based buffer over-read. When the input exceeds DOMAIN_PART_MAX_LEN, the buffer lacks '\0' termination.

## References
- https://github.com/libressl-portable/openbsd/issues/126
