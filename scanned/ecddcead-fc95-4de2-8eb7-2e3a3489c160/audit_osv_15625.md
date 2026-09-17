# [H] CVE-2019-1785

## Summary
Severity: High
Advisory: CVE-2019-1785
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-04-08
Source: https://osv.dev/vulnerability/CVE-2019-1785
Type: osv

## Details
A vulnerability in the RAR file scanning functionality of Clam AntiVirus (ClamAV) Software versions 0.101.1 and 0.101.0 could allow an unauthenticated, remote attacker to cause a denial of service condition on an affected device. The vulnerability is due to a lack of proper error-handling mechanisms when processing nested RAR files sent to an affected device. An attacker could exploit this vulnerability by sending a crafted RAR file to an affected device. An exploit could allow the attacker to view or create arbitrary files on the targeted system.

## References
- https://security.gentoo.org/glsa/201904-12
- https://bugzilla.clamav.net/show_bug.cgi?id=12284
