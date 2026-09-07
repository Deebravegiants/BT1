# [M] ProcessWire vulnerable to Cross-site Scripting

## Summary
Severity: Medium
Advisory: GHSA-8g35-prrr-gxxf
CVE: CVE-2022-40487
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-10-31
Source: https://github.com/advisories/GHSA-8g35-prrr-gxxf
Type: github-advisory

## Affected
- Packagist: `processwire/processwire` — affected >=0

## Details
ProcessWire v3.0.200 was discovered to contain multiple cross-site scripting (XSS) vulnerabilities via the Search Users and Search Pages function. These vulnerabilities allow attackers to execute arbitrary web scripts or HTML via injection of a crafted payload.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-40487
- https://gist.github.com/filipaze/32ab8683af8d82827028164e361b6e86
- https://github.com/processwire/processwire
- http://processwire.com
