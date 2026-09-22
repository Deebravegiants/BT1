# [C] Improper Restriction of XML External Entity Reference in Apache OpenNLP

## Summary
Severity: Critical
Advisory: GHSA-h22x-hm8g-rxpg
CVE: CVE-2017-12620
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-h22x-hm8g-rxpg
Type: github-advisory

## Affected
- Maven: `org.apache.opennlp:opennlp-tools` — affected >=1.5.0 <1.8.2

## Details
When loading models or dictionaries that contain XML it is possible to perform an XXE attack, since Apache OpenNLP is a library, this only affects applications that load models or dictionaries from untrusted sources. The versions 1.5.0 to 1.5.3, 1.6.0, 1.7.0 to 1.7.2, 1.8.0 to 1.8.1 of Apache OpenNLP are affected.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-12620
- http://opennlp.apache.org/news/cve-2017-12620.html
