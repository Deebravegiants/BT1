# [H] CVE-2018-1000553

## Summary
Severity: High
Advisory: CVE-2018-1000553
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-06-26
Source: https://osv.dev/vulnerability/CVE-2018-1000553
Type: osv

## Details
Trovebox version <= 4.0.0-rc6 contains a Server-Side request forgery vulnerability in webhook component that can result in read or update internal resources. This attack appear to be exploitable via HTTP request. This vulnerability appears to have been fixed in after commit 742b8ed.

## References
- https://telekomsecurity.github.io/2018/04/trovebox-vulnerabilities.html
