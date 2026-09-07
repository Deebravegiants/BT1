# [H] Apache OpenMeetings vulnerable to Uncontrolled Resource Consumption

## Summary
Severity: High
Advisory: GHSA-g3vq-f35v-vhgm
CVE: CVE-2017-7684
CWE: CWE-400
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-g3vq-f35v-vhgm
Type: github-advisory

## Affected
- Maven: `org.apache.openmeetings:openmeetings-parent` — affected >=1.0.0 <3.3.0

## Details
Apache OpenMeetings 1.0.0 doesn't check contents of files being uploaded. An attacker can cause a denial of service by uploading multiple large files to the server.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-7684
- https://github.com/apache/openmeetings
- http://markmail.org/message/v6dpmrdd6cgg66up
- http://www.securityfocus.com/bid/99584
