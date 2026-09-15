# [H] CVE-2017-12997

## Summary
Severity: High
Advisory: CVE-2017-12997
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-09-14
Source: https://osv.dev/vulnerability/CVE-2017-12997
Type: osv

## Details
The LLDP parser in tcpdump before 4.9.2 could enter an infinite loop due to a bug in print-lldp.c:lldp_private_8021_print().

## References
- http://www.securityfocus.com/bid/100914
- http://www.securitytracker.com/id/1039307
- https://support.apple.com/HT208221
- http://www.debian.org/security/2017/dsa-3971
- http://www.tcpdump.org/tcpdump-changes.txt
- https://access.redhat.com/errata/RHEA-2018:0705
- https://security.gentoo.org/glsa/201709-23
- https://github.com/the-tcpdump-group/tcpdump/commit/34cec721d39c76be1e0a600829a7b17bdfb832b6
