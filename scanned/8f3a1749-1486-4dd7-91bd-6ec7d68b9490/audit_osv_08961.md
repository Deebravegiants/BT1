# [M] CVE-2016-7077

## Summary
Severity: Medium
Advisory: CVE-2016-7077
CVSS: 4.3 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2018-09-10
Source: https://osv.dev/vulnerability/CVE-2016-7077
Type: osv

## Details
foreman before 1.14.0 is vulnerable to an information leak. It was found that Foreman form helper does not authorize options for associated objects. Unauthorized user can see names of such objects if their count is less than 6.

## References
- http://www.securityfocus.com/bid/94230
- https://theforeman.org/security.html#2016-7077
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2016-7077
- https://projects.theforeman.org/issues/16971
