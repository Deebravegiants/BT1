# [H] Server-Side Request Forgery in Databasir

## Summary
Severity: High
Advisory: CVE-2022-24862
Aliases: GHSA-r8m9-r74j-vc6m
CVSS: 7.7 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N)
Published: 2022-04-20
Source: https://osv.dev/vulnerability/CVE-2022-24862
Type: osv

## Details
Databasir is a team-oriented relational database model document management platform. Databasir 1.01 has Server-Side Request Forgery vulnerability. During the download verification process of a JDBC driver the corresponding JDBC driver download address will be downloaded first, but this address will return a response page with complete error information when accessing a non-existent URL. Attackers can take advantage of this feature for SSRF.

## References
- https://github.com/vran-dev/databasir/releases/tag/v1.0.2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/24xxx/CVE-2022-24862.json
- https://github.com/vran-dev/databasir/security/advisories/GHSA-r8m9-r74j-vc6m
- https://nvd.nist.gov/vuln/detail/CVE-2022-24862
