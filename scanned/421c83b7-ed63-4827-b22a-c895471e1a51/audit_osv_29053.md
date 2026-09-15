# [M] toy-blog Improper Input Validation vulnerability

## Summary
Severity: Medium
Advisory: CVE-2024-39313
Aliases: GHSA-rf2q-5q4q-5fwr
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2024-07-01
Source: https://osv.dev/vulnerability/CVE-2024-39313
Type: osv

## Details
toy-blog is a headless content management system implementation. Starting in version 0.5.4 and prior to version 0.6.1, articles with private visibility can be read if the reader does not set credentials for the request. Users should upgrade to 0.6.1 or later to receive a patch. No known workarounds are available.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/39xxx/CVE-2024-39313.json
- https://github.com/KisaragiEffective/toy-blog/security/advisories/GHSA-rf2q-5q4q-5fwr
- https://nvd.nist.gov/vuln/detail/CVE-2024-39313
- https://github.com/KisaragiEffective/toy-blog/commit/f13a45f68c9560124558e6bb445ad441a4cf4732
