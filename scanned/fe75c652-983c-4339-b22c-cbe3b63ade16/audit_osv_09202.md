# [M] CVE-2016-8889

## Summary
Severity: Medium
Advisory: CVE-2016-8889
CVSS: 6.2 (CVSS:3.0/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2016-10-28
Source: https://osv.dev/vulnerability/CVE-2016-8889
Type: osv

## Details
In Bitcoin Knots v0.11.0.ljr20150711 through v0.13.0.knots20160814 (fixed in v0.13.1.knots20161027), the debug console stores sensitive information including private keys and the wallet passphrase in its persistent command history.

## References
- http://www.securityfocus.com/bid/94235
- https://bitcointalk.org/index.php?topic=1618462.0
- https://github.com/bitcoinknots/bitcoin/blob/v0.13.1.knots20161027/doc/release-notes.md
