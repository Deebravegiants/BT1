# [H] Cross-Site Scripting in Prism

## Summary
Severity: High
Advisory: GHSA-wvhm-4hhf-97x9
CVE: CVE-2020-15138
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:L (CVSS_V3)
Published: 2020-08-07
Source: https://github.com/advisories/GHSA-wvhm-4hhf-97x9
Type: github-advisory

## Affected
- npm: `prismjs` — affected >=1.1.0 <1.21.0

## Details
### Impact
The easing preview of the Previewers plugin has an XSS vulnerability that allows attackers to execute arbitrary code in Safari and Internet Explorer.

This impacts all Safari and Internet Explorer users of Prism >=v1.1.0 that use the _Previewers_ plugin (>=v1.10.0) or the _Previewer: Easing_ plugin (v1.1.0 to v1.9.0).

### Patches
This problem is patched in v1.21.0.

### Workarounds
To workaround the issue without upgrading, [disable the easing preview](https://prismjs.com/plugins/previewers/#disabling-a-previewer) on all impacted code blocks. You need Prism v1.10.0 or newer to apply this workaround.

### References
The vulnerability was introduced by this [commit](https://github.com/PrismJS/prism/commit/4303c940d3d3a20e8ce7635bf23331c75060f5c5) on Sep 29, 2015 and fixed by [Masato Kinugawa](https://twitter.com/kinugawamasato) (#2506).

### For more information
If you have any questions or comments about this advisory, please [open an issue](https://github.com/PrismJS/prism/issues).

## References
- https://github.com/PrismJS/prism/security/advisories/GHSA-wvhm-4hhf-97x9
- https://nvd.nist.gov/vuln/detail/CVE-2020-15138
- https://github.com/PrismJS/prism/pull/2506/commits/7bd7de05edf71112a3a77f87901a2409c9c5c20c
- https://prismjs.com/plugins/previewers/#disabling-a-previewer
