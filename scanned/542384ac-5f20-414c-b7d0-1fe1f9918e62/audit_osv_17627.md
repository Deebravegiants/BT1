# [H] CVE-2020-1757

## Summary
Severity: High
Advisory: CVE-2020-1757
Aliases: GHSA-2w73-fqqj-c92p
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2020-04-21
Source: https://osv.dev/vulnerability/CVE-2020-1757
Type: osv

## Details
A flaw was found in all undertow-2.x.x SP1 versions prior to undertow-2.0.30.SP1, all undertow-1.x.x and undertow-2.x.x versions prior to undertow-2.1.0.Final, where the Servlet container causes servletPath to normalize incorrectly by truncating the path after semicolon which may lead to an application mapping resulting in the security bypass.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2020-1757
