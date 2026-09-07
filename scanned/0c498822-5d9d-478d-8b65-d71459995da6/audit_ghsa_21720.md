# [H] Cross Site Request Forgery in Apache JSPWiki

## Summary
Severity: High
Advisory: GHSA-4284-x26r-4hhc
CVE: CVE-2022-24947
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-02-26
Source: https://github.com/advisories/GHSA-4284-x26r-4hhc
Type: github-advisory

## Affected
- Maven: `org.apache.jspwiki:jspwiki-main` — affected >=0 <2.11.2

## Details
Apache JSPWiki user preferences form is vulnerable to CSRF attacks, which can lead to account takeover. Apache JSPWiki users should upgrade to 2.11.2 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-24947
- https://lists.apache.org/thread/txrgykjkpt80t57kzpbjo8kfrv8ss02c
- http://www.openwall.com/lists/oss-security/2022/02/25/1
