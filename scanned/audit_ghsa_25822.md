# [H] RESTEasy 4.5.5.Final in hash flooding

## Summary
Severity: High
Advisory: GHSA-37g7-8vjj-pjpj
CVE: CVE-2020-14326
CWE: CWE-400
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-03-18
Source: https://github.com/advisories/GHSA-37g7-8vjj-pjpj
Type: github-advisory

## Affected
- Maven: `org.jboss.resteasy:resteasy-bom` — affected >=0 <4.5.6.Final

## Details
A vulnerability was found in RESTEasy, where RootNode incorrectly caches routes. This issue results in hash flooding, leading to slower requests with higher CPU time spent searching and adding the entry. This flaw allows an attacker to cause a denial of service.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-14326
- https://github.com/resteasy/Resteasy/pull/2471
- https://bugzilla.redhat.com/show_bug.cgi?id=1855826
- https://github.com/resteasy/Resteasy
- https://security.netapp.com/advisory/ntap-20210713-0001
