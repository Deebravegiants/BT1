# [H] CVE-2021-37848

## Summary
Severity: High
Advisory: CVE-2021-37848
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2021-08-02
Source: https://osv.dev/vulnerability/CVE-2021-37848
Type: osv

## Details
common/password.c in Pengutronix barebox through 2021.07.0 leaks timing information because strncmp is used during hash comparison.

## References
- https://github.com/saschahauer/barebox/commit/a3337563c705bc8e0cf32f910b3e9e3c43d962ff
- https://gist.github.com/gquere/816dfadbad98745090034100a8a651eb
