# [H] PyroCMS Vulnerable to CSRF

## Summary
Severity: High
Advisory: GHSA-vg2g-698h-v9w3
CVE: CVE-2020-25263
CWE: CWE-352
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:L (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-vg2g-698h-v9w3
Type: github-advisory

## Affected
- Packagist: `pyrocms/pyrocms` — affected >=0

## Details
PyroCMS 3.7 is vulnerable to cross-site request forgery (CSRF) via the `admin/addons/uninstall/anomaly.module.blocks` URI: an arbitrary plugin will be deleted.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-25263
- https://gist.github.com/farid007/df51b0666643ec01d5571cbcc1e966e7
- https://github.com/pyrocms/pyrocms
