# [H] CVE-2017-0897

## Summary
Severity: High
Advisory: CVE-2017-0897
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2017-06-22
Source: https://osv.dev/vulnerability/CVE-2017-0897
Type: osv

## Details
ExpressionEngine version 2.x < 2.11.8 and version 3.x < 3.5.5 create an object signing token with weak entropy. Successfully guessing the token can lead to remote code execution.

## References
- http://www.securityfocus.com/bid/99242
- https://docs.expressionengine.com/latest/about/changelog.html#version-3-5-5
- https://docs.expressionengine.com/v2/about/changelog.html#version-2-11-8
- https://expressionengine.com/blog/expressionengine-3.5.5-and-2.11.8-released
- https://hackerone.com/reports/215890
