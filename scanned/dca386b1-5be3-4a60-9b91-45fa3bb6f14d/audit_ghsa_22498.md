# [H] Apache OpenMeetings allows flash content to be loaded from untrusted domains

## Summary
Severity: High
Advisory: GHSA-q52r-g8jf-wv3x
CVE: CVE-2017-7680
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-q52r-g8jf-wv3x
Type: github-advisory

## Affected
- Maven: `org.apache.openmeetings:openmeetings-parent` — affected >=1.0.0 <3.3.0

## Details
Apache OpenMeetings 1.0.0 has an overly permissive `crossdomain.xml` file. This allows for flash content to be loaded from untrusted domains.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-7680
- https://github.com/apache/openmeetings
- http://markmail.org/message/whhibri7ervbjvda
