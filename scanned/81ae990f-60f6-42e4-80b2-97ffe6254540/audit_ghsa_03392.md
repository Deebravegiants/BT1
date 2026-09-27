# [H] Allocation of Resources Without Limits or Throttling in Undertow

## Summary
Severity: High
Advisory: GHSA-g4cp-h53p-v3v8
CVE: CVE-2020-10705
CWE: CWE-770
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-04-30
Source: https://github.com/advisories/GHSA-g4cp-h53p-v3v8
Type: github-advisory

## Affected
- Maven: `io.undertow:undertow-core` — affected >=0 <2.1.1.Final

## Details
A flaw was discovered in Undertow in versions before Undertow 2.1.1.Final where certain requests to the "Expect: 100-continue" header may cause an out of memory error. This flaw may potentially lead to a denial of service.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-10705
- https://bugzilla.redhat.com/show_bug.cgi?id=1803241
- https://security.netapp.com/advisory/ntap-20220210-0014
