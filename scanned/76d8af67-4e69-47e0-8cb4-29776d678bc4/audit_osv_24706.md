# [H] CVE-2023-25350

## Summary
Severity: High
Advisory: CVE-2023-25350
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-03-24
Source: https://osv.dev/vulnerability/CVE-2023-25350
Type: osv

## Details
Faveo Helpdesk 1.0-1.11.1 is vulnerable to SQL Injection. When the user logs in through the login box, he has no judgment on the validity of the user's input data. The parameters passed from the front end to the back end are controllable, which will lead to SQL injection.

## References
- https://gist.github.com/Whitehat-Su/8402323c00ea93b4abc21ab9a372101e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/25xxx/CVE-2023-25350.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-25350
- https://github.com/ladybirdweb/faveo-helpdesk/issues/7827
