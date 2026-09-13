# [H] CVE-2017-2659

## Summary
Severity: High
Advisory: CVE-2017-2659
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2019-03-21
Source: https://osv.dev/vulnerability/CVE-2017-2659
Type: osv

## Details
It was found that dropbear before version 2013.59 with GSSAPI leaks whether given username is valid or invalid. When an invalid username is given, the GSSAPI authentication failure was incorrectly counted towards the maximum allowed number of password attempts.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2017-2659
- https://secure.ucc.asn.au/hg/dropbear/rev/d7784616409a#l1.86
