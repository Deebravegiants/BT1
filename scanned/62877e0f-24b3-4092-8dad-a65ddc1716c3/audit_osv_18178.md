# [C] CVE-2020-24791

## Summary
Severity: Critical
Advisory: CVE-2020-24791
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-03-10
Source: https://osv.dev/vulnerability/CVE-2020-24791
Type: osv

## Details
FUEL CMS 1.4.8 allows SQL injection via the 'fuel_replace_id' parameter in pages/replace/1. Exploiting this issue could allow an attacker to compromise the application, access or modify data, or exploit latent vulnerabilities in the underlying database.

## References
- https://github.com/daylightstudio/FUEL-CMS/issues/561
- https://github.com/leerina/vulnerability/blob/master/Fuel%20CMS%201.4.8%20SQLi%20vulnerability.txt
- https://www.exploit-db.com/exploits/48778
