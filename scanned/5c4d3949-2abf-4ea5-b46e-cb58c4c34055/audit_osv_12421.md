# [M] CVE-2018-11782

## Summary
Severity: Medium
Advisory: CVE-2018-11782
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-09-26
Source: https://osv.dev/vulnerability/CVE-2018-11782
Type: osv

## Details
In Apache Subversion versions up to and including 1.9.10, 1.10.4, 1.12.0, Subversion's svnserve server process may exit when a well-formed read-only request produces a particular answer. This can lead to disruption for users of the server.

## References
- http://subversion.apache.org/security/CVE-2018-11782-advisory.txt
