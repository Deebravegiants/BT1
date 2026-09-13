# [H] Special top object can be used to access Struts' internals

## Summary
Severity: High
Advisory: GHSA-4qgj-9mvg-3929
CVE: CVE-2015-5209
CWE: CWE-20
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-4qgj-9mvg-3929
Type: github-advisory

## Affected
- Maven: `org.apache.struts:struts2-core` — affected >=0 <2.3.24.1

## Details
ValueStack defines special top object which represents root of execution context. It can be used to manipulate Struts' internals or can be used to affect container's settings. Applying better regex which includes pattern to exclude request parameters trying to use top object. This issue was patched in Struts 2.3.24.1.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-5209
- https://security.netapp.com/advisory/ntap-20180629-0002
- https://struts.apache.org/docs/s2-026.html
