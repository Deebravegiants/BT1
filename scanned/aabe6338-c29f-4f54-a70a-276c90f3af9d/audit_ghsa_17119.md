# [H] Winter CMS Server-Side Template Injection (SSTI) vulnerability

## Summary
Severity: High
Advisory: GHSA-8r5j-gm3j-cx9c
CVE: CVE-2024-29686
CWE: CWE-75, CWE-97
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-03-29
Source: https://github.com/advisories/GHSA-8r5j-gm3j-cx9c
Type: github-advisory

## Affected
- Packagist: `wintercms/winter` — affected >=0

## Details
Server-side Template Injection (SSTI) vulnerability in Winter CMS v.1.2.3 allows a remote attacker to execute arbitrary code via a crafted payload to the CMS Pages field and Plugin components.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-29686
- https://forum.ksec.co.uk/t/webapps-winter-cms-1-2-3-server-side-template-injection-ssti-authenticated/2779
- https://github.com/wintercms/winter
- https://wintercms.com/docs/v1.2/docs/cms/themes#template-structure
- https://www.exploit-db.com/exploits/51893
