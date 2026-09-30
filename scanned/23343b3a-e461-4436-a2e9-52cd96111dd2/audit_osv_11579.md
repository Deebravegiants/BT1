# [H] CVE-2017-8825

## Summary
Severity: High
Advisory: CVE-2017-8825
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-05-08
Source: https://osv.dev/vulnerability/CVE-2017-8825
Type: osv

## Details
A null dereference vulnerability has been found in the MIME handling component of LibEtPan before 1.8, as used in MailCore and MailCore 2. A crash can occur in low-level/imf/mailimf.c during a failed parse of a Cc header containing multiple e-mail addresses.

## References
- https://github.com/dinhviethoa/libetpan/issues/274
- https://github.com/dinhviethoa/libetpan/releases/tag/1.8
- https://github.com/dinhviethoa/libetpan/commit/1fe8fbc032ccda1db9af66d93016b49c16c1f22d
