# [H] Missing encryption in Apache Directory Studio

## Summary
Severity: High
Advisory: GHSA-4x25-f45x-grv5
CVE: CVE-2021-33900
CWE: CWE-311, CWE-319
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2021-08-09
Source: https://github.com/advisories/GHSA-4x25-f45x-grv5
Type: github-advisory

## Affected
- Maven: `org.apache.directory.studio:org.apache.directory.studio.parent` — affected >=0 <2.0.0.v20210717-M17

## Details
While investigating DIRSTUDIO-1219 it was noticed that configured StartTLS encryption was not applied when any SASL authentication mechanism (DIGEST-MD5, GSSAPI) was used. While investigating DIRSTUDIO-1220 it was noticed that any configured SASL confidentiality layer was not applied. This issue affects Apache Directory Studio version 2.0.0.v20210213-M16 and prior versions.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-33900
- https://lists.apache.org/thread.html/rb1dbcc43a5b406e45d335343a1704f4233de613140a01929d102fdc9%40%3Cusers.directory.apache.org%3E
