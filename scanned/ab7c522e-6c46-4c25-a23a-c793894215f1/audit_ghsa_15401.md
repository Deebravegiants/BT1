# [H] Alpine allows URL access filter bypass

## Summary
Severity: High
Advisory: GHSA-2w4p-2hf7-gh8x
CVE: CVE-2022-23553
CWE: CWE-863
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-08-05
Source: https://github.com/advisories/GHSA-2w4p-2hf7-gh8x
Type: github-advisory

## Affected
- Maven: `us.springett:alpine` — affected >=0 <1.10.4

## Details
Alpine is a scaffolding library in Java. Alpine prior to version 1.10.4 allows URL access filter bypass. This issue has been fixed in version 1.10.4. There are no known workarounds.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-23553
- https://github.com/stevespringett/Alpine/commit/a7432184b9137ea095799a77f9ced370553acbd7
- https://github.com/stevespringett/Alpine
- https://github.com/stevespringett/Alpine/blob/alpine-parent-1.10.2/alpine/src/main/java/alpine/filters/BlacklistUrlFilter.java#L107-L121
- https://github.com/stevespringett/Alpine/blob/alpine-parent-1.10.2/alpine/src/main/java/alpine/filters/WhitelistUrlFilter.java#L115-L127
- https://github.com/stevespringett/Alpine/releases/tag/alpine-parent-1.10.4
- https://securitylab.github.com/advisories
- https://securitylab.github.com/advisories/GHSL-2021-1009-Alpine
