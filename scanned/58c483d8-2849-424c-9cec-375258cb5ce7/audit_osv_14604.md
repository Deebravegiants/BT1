# [M] CVE-2019-10242

## Summary
Severity: Medium
Advisory: CVE-2019-10242
CVSS: 5.3 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2019-04-09
Source: https://osv.dev/vulnerability/CVE-2019-10242
Type: osv

## Details
In Eclipse Kura versions up to 4.0.0, the SkinServlet did not checked the path passed during servlet call, potentially allowing path traversal in get requests for a limited number of file types.

## References
- http://www.securityfocus.com/bid/107844
- https://bugs.eclipse.org/bugs/show_bug.cgi?id=545835
