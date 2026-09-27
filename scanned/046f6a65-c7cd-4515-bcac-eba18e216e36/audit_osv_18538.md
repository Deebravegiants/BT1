# [C] CVE-2020-28490

## Summary
Severity: Critical
Advisory: CVE-2020-28490
Aliases: GHSA-6qpr-9mc5-7gch
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-02-18
Source: https://osv.dev/vulnerability/CVE-2020-28490
Type: osv

## Details
The package async-git before 1.13.2 are vulnerable to Command Injection via shell meta-characters (back-ticks). For example: git.reset('atouch HACKEDb')

## References
- https://github.com/omrilotan/async-git/commit/d1950a5021f4e19d92f347614be0d85ce991510d
- https://github.com/omrilotan/async-git/pull/14
- https://snyk.io/vuln/SNYK-JS-ASYNCGIT-1064877
