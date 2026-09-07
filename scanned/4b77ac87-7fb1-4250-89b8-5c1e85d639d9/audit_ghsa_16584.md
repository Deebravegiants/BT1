# [H] ansibleguy-webui Cross-site Scripting vulnerability

## Summary
Severity: High
Advisory: GHSA-927p-xrc2-x2gj
CVE: CVE-2024-36110
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:L/A:L (CVSS_V3)
Published: 2024-05-28
Source: https://github.com/advisories/GHSA-927p-xrc2-x2gj
Type: github-advisory

## Affected
- PyPI: `ansibleguy-webui` — affected >=0 <0.0.21

## Details
### Impact
Multiple forms in version <0.0.21 allowed injection of HTML elements.
These are returned to the user after executing job actions and thus evaluated by the browser.

### Patches
We recommend to upgrade to version >= [0.0.21](https://github.com/ansibleguy/webui/releases/tag/0.0.21)

### References

* [Report](https://github.com/ansibleguy/webui/files/15358522/Report.pdf)
* [GitHub Issue 44](https://github.com/ansibleguy/webui/issues/44)

## References
- https://github.com/ansibleguy/webui/security/advisories/GHSA-927p-xrc2-x2gj
- https://nvd.nist.gov/vuln/detail/CVE-2024-36110
- https://github.com/ansibleguy/webui/issues/44
- https://github.com/ansibleguy/webui/commit/7737b47e7f7ddbfec7b1418c724598363718d522
- https://github.com/ansibleguy/webui
- https://github.com/ansibleguy/webui/files/15358522/Report.pdf
