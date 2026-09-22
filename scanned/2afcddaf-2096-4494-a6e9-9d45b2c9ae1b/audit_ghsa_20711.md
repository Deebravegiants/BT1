# [H] 4thline cling uPnP protocol issue can lead to denial of service

## Summary
Severity: High
Advisory: GHSA-c438-6f6r-pg8w
CVE: CVE-2020-23622
CWE: CWE-918
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-08-16
Source: https://github.com/advisories/GHSA-c438-6f6r-pg8w
Type: github-advisory

## Affected
- Maven: `org.fourthline.cling:cling-core` — affected >=2.0.0

## Details
An issue in the UPnP protocol in 4thline cling 2.0.0 through 2.1.2 allows remote attackers to cause a denial of service via an unchecked `CALLBACK` parameter in the request header. As of 2022, 4thline cling is no longer supported by the maintainers.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-23622
- https://github.com/4thline/cling/issues/253
- https://github.com/4thline/cling
- https://zh-cn.tenable.com/blog/cve-2020-12695-callstranger-vulnerability-in-universal-plug-and-play-upnp-puts-billions-of?tns_redirect=true
