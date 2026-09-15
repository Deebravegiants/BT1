# [H] CVE-2021-37847

## Summary
Severity: High
Advisory: CVE-2021-37847
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2021-08-02
Source: https://osv.dev/vulnerability/CVE-2021-37847
Type: osv

## Details
crypto/digest.c in Pengutronix barebox through 2021.07.0 leaks timing information because memcmp is used during digest verification.

## References
- https://github.com/saschahauer/barebox/commit/0a9f9a7410681e55362f8311537ebc7be9ad0fbe
- https://gist.github.com/gquere/816dfadbad98745090034100a8a651eb
