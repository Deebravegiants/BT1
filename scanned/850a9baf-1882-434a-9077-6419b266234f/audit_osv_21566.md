# [H] CVE-2021-44082

## Summary
Severity: High
Advisory: CVE-2021-44082
CVSS: 8.3 (CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:C/C:H/I:H/A:H)
Published: 2022-03-29
Source: https://osv.dev/vulnerability/CVE-2021-44082
Type: osv

## Details
textpattern 4.8.7 is vulnerable to Cross Site Scripting (XSS) via /textpattern/index.php,Body. A remote and unauthenticated attacker can use XSS to trigger remote code execution by uploading a webshell. To do so they must first steal the CSRF token before submitting a file upload request.

## References
- https://www.cornerpirate.com
- https://www.pentest.co.uk
- https://pentest.co.uk/labs/leveraging-xss-to-get-rce-in-textpattern/
