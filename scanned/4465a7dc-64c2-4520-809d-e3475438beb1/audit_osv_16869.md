# [M] CVE-2020-10105

## Summary
Severity: Medium
Advisory: CVE-2020-10105
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2020-03-05
Source: https://osv.dev/vulnerability/CVE-2020-10105
Type: osv

## Details
An issue was discovered in Zammad 3.0 through 3.2. It returns source code of static resources when submitting an OPTIONS request, rather than a GET request. Disclosure of source code allows for an attacker to formulate more precise attacks. Source code was disclosed for the file 404.html (/zammad/public/404.html)

## References
- https://zammad.com/news/security-advisory-zaa-2020-09
