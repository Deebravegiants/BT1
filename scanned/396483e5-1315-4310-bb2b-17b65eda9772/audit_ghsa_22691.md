# [M] undertow Race Condition vulnerability

## Summary
Severity: Medium
Advisory: GHSA-mfhv-gwf8-4m88
CVE: CVE-2021-3597
CWE: CWE-362
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-05-25
Source: https://github.com/advisories/GHSA-mfhv-gwf8-4m88
Type: github-advisory

## Affected
- Maven: `io.undertow:undertow-core` — affected >=2.1.0 <2.2.9.Final
- Maven: `io.undertow:undertow-core` — affected >=0 <2.0.39.Final

## Details
A flaw was found in undertow. The HTTP2SourceChannel fails to write the final frame under some circumstances, resulting in a denial of service. The highest threat from this vulnerability is availability. This flaw affects Undertow versions prior to 2.0.35.SP1, prior to 2.2.6.SP1, prior to 2.2.7.SP1, prior to 2.0.36.SP1, prior to 2.2.9.Final and prior to 2.0.39.Final.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-3597
- https://bugzilla.redhat.com/show_bug.cgi?id=1970930
- https://github.com/undertow-io/undertow
- https://security.netapp.com/advisory/ntap-20220804-0003
