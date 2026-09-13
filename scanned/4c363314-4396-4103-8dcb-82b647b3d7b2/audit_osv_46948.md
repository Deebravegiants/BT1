# [H] CVE-2015-8400

## Summary
Severity: High
Advisory: CVE-2015-8400
CVSS: 7.4 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:N/I:H/A:N)
Published: 2016-01-12
Source: https://osv.dev/vulnerability/CVE-2015-8400
Type: osv

## Details
The HTTPS fallback implementation in Shell In A Box (aka shellinabox) before 2.19 makes it easier for remote attackers to conduct DNS rebinding attacks via the "/plain" URL.

## References
- https://github.com/shellinabox/shellinabox/issues/355
- https://github.com/shellinabox/shellinabox/releases/tag/v2.19
- http://lists.fedoraproject.org/pipermail/package-announce/2016-January/175117.html
- http://lists.fedoraproject.org/pipermail/package-announce/2016-January/175224.html
- http://www.openwall.com/lists/oss-security/2015/12/02/6
- http://www.openwall.com/lists/oss-security/2015/12/02/7
