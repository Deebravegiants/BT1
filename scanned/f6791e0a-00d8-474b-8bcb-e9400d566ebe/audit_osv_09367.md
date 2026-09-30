# [H] CVE-2016-9597

## Summary
Severity: High
Advisory: CVE-2016-9597
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-07-30
Source: https://osv.dev/vulnerability/CVE-2016-9597
Type: osv

## Details
It was found that Red Hat JBoss Core Services erratum RHSA-2016:2957 for CVE-2016-3705 did not actually include the fix for the issue found in libxml2, making it vulnerable to a Denial of Service attack due to a Stack Overflow. This is a regression CVE for the same issue as CVE-2016-3705.

## References
- http://www.securityfocus.com/bid/98567
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2016-9597
