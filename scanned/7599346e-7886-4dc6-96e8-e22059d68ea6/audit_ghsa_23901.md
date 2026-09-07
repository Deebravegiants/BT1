# [M] LavaLite Stored Cross-site Scripting vulnerability

## Summary
Severity: Medium
Advisory: GHSA-3cfg-rxh6-h2rh
CVE: CVE-2020-36397
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-3cfg-rxh6-h2rh
Type: github-advisory

## Affected
- Packagist: `lavalite/cms` — affected >=0

## Details
A stored cross site scripting (XSS) vulnerability in the `/admin/contact/contact` component of LavaLite 5.8.0 allows authenticated attackers to execute arbitrary web scripts or HTML via a crafted payload entered into the `New` parameter.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-36397
- https://github.com/LavaLite/cms/issues/323
