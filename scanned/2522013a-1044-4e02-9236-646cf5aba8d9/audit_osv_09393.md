# [H] CVE-2016-9752

## Summary
Severity: High
Advisory: CVE-2016-9752
CVSS: 8.6 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:C/C:N/I:H/A:N)
Published: 2016-12-01
Source: https://osv.dev/vulnerability/CVE-2016-9752
Type: osv

## Details
In Serendipity before 2.0.5, an attacker can bypass SSRF protection by using a malformed IP address (e.g., http://127.1) or a 30x (aka Redirection) HTTP status code.

## References
- http://www.securityfocus.com/bid/94622
- https://blog.s9y.org/archives/271-Serendipity-2.0.5-and-2.1-beta3-released.html
- https://github.com/s9y/Serendipity/commit/fbdd50a448ed87ba34ea8c56446b8f1873eadd6f
