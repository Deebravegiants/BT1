# [M] CVE-2016-5390

## Summary
Severity: Medium
Advisory: CVE-2016-5390
CVSS: 5.3 (CVSS:3.0/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2016-08-19
Source: https://osv.dev/vulnerability/CVE-2016-5390
Type: osv

## Details
Foreman before 1.11.4 and 1.12.x before 1.12.1 allow remote authenticated users with the view_hosts permission containing a filter to obtain sensitive network interface information via a request to API routes beneath "hosts," as demonstrated by a GET request to api/v2/hosts/secrethost/interfaces.

## References
- http://www.securityfocus.com/bid/91770
- https://theforeman.org/security.html#2016-5390
- https://bugzilla.redhat.com/show_bug.cgi?id=1355728
- http://projects.theforeman.org/issues/15653
