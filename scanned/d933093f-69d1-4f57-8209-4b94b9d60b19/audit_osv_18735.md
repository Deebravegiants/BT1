# [C] CVE-2020-35674

## Summary
Severity: Critical
Advisory: CVE-2020-35674
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-09-29
Source: https://osv.dev/vulnerability/CVE-2020-35674
Type: osv

## Details
BigProf Online Invoicing System before 2.9 suffers from an unauthenticated SQL Injection found in /membership_passwordReset.php (the endpoint that is responsible for issuing self-service password resets). An unauthenticated attacker is able to send a request containing a crafted payload that can result in sensitive information being extracted from the database, eventually leading into an application takeover. This vulnerability was introduced as a result of the developer trying to roll their own sanitization implementation in order to allow the application to be used in legacy environments.

## References
- https://labs.ingredous.com/2020/07/13/ois-sqli/
