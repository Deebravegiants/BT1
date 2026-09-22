# [H] Pimcore CMS Twig Sandbox Bypass via SecurityPolicy checkMethodAllowed

## Summary
Severity: High
Advisory: GHSA-7p36-fq2r-4h7r
CVE: CVE-2026-11407
CWE: CWE-1336
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-06-17
Source: https://github.com/advisories/GHSA-7p36-fq2r-4h7r
Type: github-advisory

## Affected
- Packagist: `pimcore/pimcore` — affected >=12.0.0-RC1
- Packagist: `pimcore/pimcore` — affected >=0

## Details
Pimcore CMS/DXP version 12.3.8 contains a sandbox bypass vulnerability that allows authenticated administrative attackers to execute arbitrary methods on PHP objects by exploiting empty checkMethodAllowed() and checkPropertyAllowed() implementations in the custom Twig SecurityPolicy. Attackers can supply malicious Twig templates through the DataObject ClassDefinition Layout\Text component to perform arbitrary file reads, execute arbitrary database queries, and potentially achieve remote code execution via PHP object gadget chains, with the pimcore_* function wildcard further broadening the bypass to all Pimcore Twig functions.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-11407
- https://github.com/pimcore/pimcore/pull/19193
- https://github.com/pimcore/pimcore/commit/fffa7f6396329e88610db70a8652529bbc734892
- https://github.com/pimcore/pimcore
- https://www.vulncheck.com/advisories/pimcore-cms-twig-sandbox-bypass-via-securitypolicy-checkmethodallowed
