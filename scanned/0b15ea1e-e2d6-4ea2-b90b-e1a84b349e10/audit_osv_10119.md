# [H] CVE-2017-13745

## Summary
Severity: High
Advisory: CVE-2017-13745
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-08-29
Source: https://osv.dev/vulnerability/CVE-2017-13745
Type: osv

## Details
There is a reachable assertion abort in the function jpc_dec_process_sot() in jpc/jpc_dec.c in JasPer 2.0.12 that will lead to a remote denial of service attack by triggering an unexpected jpc_ppmstabtostreams return value, a different vulnerability than CVE-2018-9154.

## References
- http://www.securityfocus.com/bid/100514
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/N4ALB4SXHURLVWKAOKYRNJXPABW3M22M/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/UPOVZTSIQPW2H4AFLMI3LHJEZGBVEQET/
- https://www.oracle.com/security-alerts/cpuapr2020.html
- https://security.gentoo.org/glsa/201908-03
- https://www.oracle.com/technetwork/security-advisory/cpujan2019-5072801.html
- https://bugzilla.redhat.com/show_bug.cgi?id=1485274
