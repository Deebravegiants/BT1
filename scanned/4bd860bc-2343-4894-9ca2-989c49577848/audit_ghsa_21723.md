# [H] Path Traversal

## Summary
Severity: High
Advisory: GHSA-cp67-8w3w-6h9c
CVE: CVE-2020-14366
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-02-09
Source: https://github.com/advisories/GHSA-cp67-8w3w-6h9c
Type: github-advisory

## Affected
- Maven: `org.keycloak:keycloak-parent` — affected >=0 <12.0.0

## Details
A vulnerability was found in keycloak, where path traversal using URL-encoded path segments in the request is possible because the resources endpoint applies a transformation of the url path to the file path. Only few specific folder hierarchies can be exposed by this flaw

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-14366
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2020-14366
