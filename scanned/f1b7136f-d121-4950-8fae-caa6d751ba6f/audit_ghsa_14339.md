# [C] Remote code execution in Voyager

## Summary
Severity: Critical
Advisory: GHSA-2x3r-7jgm-gh8x
CVE: CVE-2020-36070
CWE: CWE-281
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-04-26
Source: https://github.com/advisories/GHSA-2x3r-7jgm-gh8x
Type: github-advisory

## Affected
- Packagist: `tcg/voyager` — affected >=0

## Details
Insecure Permission vulnerability found in Voyager v.1.4 and before allows a remote attacker to execute arbitrary code via a crafted .php file to the media component.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-36070
- https://github.com/the-control-group/voyager
