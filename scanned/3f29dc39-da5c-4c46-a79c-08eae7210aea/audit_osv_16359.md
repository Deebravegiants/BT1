# [M] CVE-2019-6110

## Summary
Severity: Medium
Advisory: CVE-2019-6110
CVSS: 6.8 (CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:N)
Published: 2019-01-31
Source: https://osv.dev/vulnerability/CVE-2019-6110
Type: osv

## Details
In OpenSSH 7.9, due to accepting and displaying arbitrary stderr output from the server, a malicious server (or Man-in-The-Middle attacker) can manipulate the client output, for example to use ANSI control codes to hide additional files being transferred.

## References
- https://cvsweb.openbsd.org/src/usr.bin/ssh/progressmeter.c
- https://cvsweb.openbsd.org/src/usr.bin/ssh/scp.c
- https://security.gentoo.org/glsa/201903-16
- https://security.netapp.com/advisory/ntap-20190213-0001/
- https://sintonen.fi/advisories/scp-client-multiple-vulnerabilities.txt
- https://cert-portal.siemens.com/productcert/pdf/ssa-412672.pdf
- https://www.exploit-db.com/exploits/46193/
