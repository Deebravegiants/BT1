# [H] CVE-2018-16301

## Summary
Severity: High
Advisory: CVE-2018-16301
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-10-03
Source: https://osv.dev/vulnerability/CVE-2018-16301
Type: osv

## Details
The command-line argument parser in tcpdump before 4.99.0 has a buffer overflow in tcpdump.c:read_infile(). To trigger this vulnerability the attacker needs to create a 4GB file on the local filesystem and to specify the file name as the value of the -F command-line argument of tcpdump.

## References
- https://github.com/the-tcpdump-group/tcpdump/commit/ad7c25bc0decf96dc7768c9e903734d38528b1bd
