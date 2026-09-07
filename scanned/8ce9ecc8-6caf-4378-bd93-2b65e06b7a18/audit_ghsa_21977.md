# [H] Denial of service in Undertow

## Summary
Severity: High
Advisory: GHSA-rhcw-wjcm-9h6g
CVE: CVE-2020-27782
CWE: CWE-400
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-02-09
Source: https://github.com/advisories/GHSA-rhcw-wjcm-9h6g
Type: github-advisory

## Affected
- Maven: `io.undertow:undertow-core` — affected >=2.1.0 <2.1.5
- Maven: `io.undertow:undertow-core` — affected >=0 <2.0.33

## Details
A flaw was found in the Undertow AJP connector. Malicious requests and abrupt connection closes could be triggered by an attacker using query strings with non-RFC compliant characters resulting in a denial of service. The highest threat from this vulnerability is to system availability. This affects Undertow 2.1.5.SP1, 2.0.33.SP2, and 2.2.3.SP1.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-27782
- https://github.com/undertow-io/undertow/pull/997/commits/98a9ab7f2d7fe7a7254eaf17d47816c452169c90
- https://bugzilla.redhat.com/show_bug.cgi?id=1901304
- https://issues.redhat.com/browse/UNDERTOW-1813
