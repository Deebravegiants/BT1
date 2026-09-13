# [C] XML External Entity (XXE) vulnerability in bw-calendar-engine

## Summary
Severity: Critical
Advisory: GHSA-xmvg-w4f9-99r7
CVE: CVE-2018-1000836
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2018-12-20
Source: https://github.com/advisories/GHSA-xmvg-w4f9-99r7
Type: github-advisory

## Affected
- Maven: `org.bedework.caleng:bw-calendar-engine` — affected >=0

## Details
bw-calendar-engine version <= bw-calendar-engine-3.12.0 contains a XML External Entity (XXE) vulnerability in IscheduleClient XML Parser that can result in Disclosure of confidential data, denial of service, SSRF, port scanning. This attack appear to be exploitable via Man in the Middle or malicious server.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1000836
- https://github.com/Bedework/bw-calendar-engine/issues/3
- https://0dd.zone/2018/10/28/bw-calendar-engine-XXE-MitM
- https://github.com/Bedework/bw-calendar-engine
- https://github.com/advisories/GHSA-xmvg-w4f9-99r7
