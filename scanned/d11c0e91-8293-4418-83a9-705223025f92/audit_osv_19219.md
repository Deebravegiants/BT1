# [M] CVE-2020-8821

## Summary
Severity: Medium
Advisory: CVE-2020-8821
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N)
Published: 2020-10-12
Source: https://osv.dev/vulnerability/CVE-2020-8821
Type: osv

## Details
An Improper Data Validation Vulnerability exists in Webmin 1.941 and earlier affecting the Command Shell Endpoint. A user may enter HTML code into the Command field and submit it. Then, after visiting the Action Logs Menu and displaying logs, the HTML code will be rendered (however, JavaScript is not executed). Changes are kept across users.

## References
- https://www.webmin.com/security.html
