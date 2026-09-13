# [H] CVE-2017-13750

## Summary
Severity: High
Advisory: CVE-2017-13750
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-08-29
Source: https://osv.dev/vulnerability/CVE-2017-13750
Type: osv

## Details
There is a reachable assertion abort in the function jpc_dec_process_siz() in jpc/jpc_dec.c:1296 in JasPer 2.0.12 that will lead to a remote denial of service attack.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/N4ALB4SXHURLVWKAOKYRNJXPABW3M22M/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/UPOVZTSIQPW2H4AFLMI3LHJEZGBVEQET/
- http://www.securityfocus.com/bid/100514
- https://security.gentoo.org/glsa/201908-03
- https://bugzilla.redhat.com/show_bug.cgi?id=1485280
