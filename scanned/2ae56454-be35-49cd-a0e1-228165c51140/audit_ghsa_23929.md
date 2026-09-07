# [M] Cloudera HUE Account Enumeration

## Summary
Severity: Medium
Advisory: GHSA-rxfp-8jmr-xc95
CVE: CVE-2016-4947
CWE: CWE-200
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-rxfp-8jmr-xc95
Type: github-advisory

## Affected
- npm: `gethue` — affected >=0

## Details
Cloudera HUE 3.9.0 and earlier allows remote attackers to enumerate user accounts via a request to `desktop/api/users/autocomplete`.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-4947
- https://github.com/cloudera/hue
- https://web.archive.org/web/20210123183622/http://www.securityfocus.com/bid/93880
- http://2016.hack.lu/archive/2016/Wavestone%20-%20Hack.lu%202016%20-%20Hadoop%20safari%20-%20Hunting%20for%20vulnerabilities%20-%20v1.0.pdf
