# [M] Sanitization bypass using HTML Entities in marked

## Summary
Severity: Medium
Advisory: GHSA-vfvf-mqq8-rwqc
CVE: CVE-2016-10531
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2019-02-18
Source: https://github.com/advisories/GHSA-vfvf-mqq8-rwqc
Type: github-advisory

## Affected
- npm: `marked` — affected >=0 <0.3.6

## Details
Affected versions of `marked` are susceptible to a cross-site scripting vulnerability in link components when `sanitize:true` is configured. 

## Proof of Concept

This flaw exists because link URIs containing HTML entities get processed in an abnormal manner. Any HTML Entities get parsed on a best-effort basis and included in the resulting link, while if that parsing fails that character is omitted.

For example:

A link URI such as
```
javascript&#x58document;alert&#40;1&#41;
```
Renders a valid link that when clicked will execute `alert(1)`.


## Recommendation

Update to version 0.3.6 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-10531
- https://github.com/chjj/marked/pull/592
- https://github.com/chjj/marked/pull/592/commits/2cff85979be8e7a026a9aca35542c470cf5da523
- https://github.com/advisories/GHSA-vfvf-mqq8-rwqc
- https://www.npmjs.com/advisories/101
