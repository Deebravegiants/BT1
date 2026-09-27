# [C] exist-db:exist-core XML External Entity (XXE) vulnerability

## Summary
Severity: Critical
Advisory: GHSA-jxm5-5xcw-h57q
CVE: CVE-2018-1000823
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2018-12-20
Source: https://github.com/advisories/GHSA-jxm5-5xcw-h57q
Type: github-advisory

## Affected
- Maven: `org.exist-db:exist-core` — affected >=0 <5.1.0

## Details
exist version <= 5.0.0-RC4 contains a XML External Entity (XXE) vulnerability in XML Parser for REST Server that can result in Disclosure of confidential data, denial of service, SSRF, port scanning.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1000823
- https://github.com/eXist-db/exist/issues/2180
- https://github.com/eXist-db/exist/pull/2243
- https://github.com/eXist-db/exist/pull/2247
- https://github.com/eXist-db/exist/commit/1c3f0aec14d00bdbca175713af70cb7c7b868e9f
- https://github.com/eXist-db/exist/commit/b210f9fbf379b68842f2b055dda80d7e7479e96f
- https://0dd.zone/2018/10/27/exist-XXE
- https://github.com/advisories/GHSA-jxm5-5xcw-h57q
- https://github.com/eXist-db/exist
