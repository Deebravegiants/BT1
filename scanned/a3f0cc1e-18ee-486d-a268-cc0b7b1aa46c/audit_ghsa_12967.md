# [M] PrestaShop file access through path traversal

## Summary
Severity: Medium
Advisory: GHSA-hpf4-v7v2-95p2
CVE: CVE-2023-39528
CWE: CWE-22
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:N/I:H/A:N (CVSS_V3)
Published: 2023-08-09
Source: https://github.com/advisories/GHSA-hpf4-v7v2-95p2
Type: github-advisory

## Affected
- Packagist: `prestashop/prestashop` — affected >=0 <8.1.1

## Details
### Impact
`displayAjaxEmailHTML` method can be used to read any file on the server, potentially even outside of the project if the server is not correctly configured.

This vulnerability can be exacerbated when coupled with [CWE-502](https://cwe.mitre.org/data/definitions/502.html), which pertains to the Deserialization of Untrusted Data. Such a combination could potentially lead to a Remote Code Execution (RCE) vulnerability

### Patches
8.1.1

### Found by
Aleksey Solovev (Positive Technologies)

### Workarounds

### References

## References
- https://github.com/PrestaShop/PrestaShop/security/advisories/GHSA-hpf4-v7v2-95p2
- https://nvd.nist.gov/vuln/detail/CVE-2023-39528
- https://github.com/PrestaShop/PrestaShop/commit/11de3a84322fa4ecd0995ac40d575db61804724c
- https://github.com/PrestaShop/PrestaShop
