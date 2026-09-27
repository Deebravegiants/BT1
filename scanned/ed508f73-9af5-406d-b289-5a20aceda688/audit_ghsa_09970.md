# [M] ShowDoc has an Injection vulnerability

## Summary
Severity: Medium
Advisory: GHSA-fm5r-cj7v-rj2c
CVE: CVE-2026-6982
CWE: CWE-74
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2026-04-25
Source: https://github.com/advisories/GHSA-fm5r-cj7v-rj2c
Type: github-advisory

## Affected
- Packagist: `showdoc/showdoc` — affected >=0 <3.8.1

## Details
A vulnerability was determined in star7th ShowDoc up to 2.10.10/3.6.2/3.8.0. Affected by this vulnerability is an unknown functionality of the file server/Application/Api/Controller/PageController.class.PHP of the component API Page Sort Endpoint. Executing a manipulation of the argument pages can lead to sql injection. The attack may be launched remotely. Upgrading to version 3.8.1 addresses this issue. It is suggested to upgrade the affected component. According to the researcher, "[t]he vendor explicitly stated they will not backport patches to the older affected versions."

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-6982
- https://gist.github.com/saDL0w/555e19668264f98d96259ad47ea33811
- https://github.com/star7th/showdoc
- https://github.com/star7th/showdoc/releases/tag/v3.8.1
- https://vuldb.com/submit/795528
- https://vuldb.com/vuln/359525
- https://vuldb.com/vuln/359525/cti
