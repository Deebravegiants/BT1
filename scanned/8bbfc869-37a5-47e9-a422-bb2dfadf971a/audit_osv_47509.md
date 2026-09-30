# [M] CVE-2016-7409

## Summary
Severity: Medium
Advisory: CVE-2016-7409
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2017-03-03
Source: https://osv.dev/vulnerability/CVE-2016-7409
Type: osv

## Details
The dbclient and server in Dropbear SSH before 2016.74, when compiled with DEBUG_TRACE, allows local users to read process memory via the -v argument, related to a failed remote ident.

## References
- http://www.securityfocus.com/bid/92973
- https://bugzilla.redhat.com/show_bug.cgi?id=1376353
- http://www.openwall.com/lists/oss-security/2016/09/15/2
- https://secure.ucc.asn.au/hg/dropbear/rev/6a14b1f6dc04
- https://security.gentoo.org/glsa/201702-23
