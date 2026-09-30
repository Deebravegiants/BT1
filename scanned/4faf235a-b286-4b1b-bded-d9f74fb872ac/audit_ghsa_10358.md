# [M] pypdf: Possible long runtimes for wrong size values in incremental mode

## Summary
Severity: Medium
Advisory: GHSA-4pxv-j86v-mhcw
CVE: CVE-2026-41313
CWE: CWE-834
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-04-16
Source: https://github.com/advisories/GHSA-4pxv-j86v-mhcw
Type: github-advisory

## Affected
- PyPI: `pypdf` — affected >=0 <6.10.2

## Details
### Impact
An attacker who uses this vulnerability can craft a PDF which leads to long runtimes. This requires loading a PDF with a large trailer `/Size` value in incremental mode.

### Patches
This has been fixed in [pypdf==6.10.2](https://github.com/py-pdf/pypdf/releases/tag/6.10.2).

### Workarounds
If you cannot upgrade yet, consider applying the changes from PR [#3735](https://github.com/py-pdf/pypdf/pull/3735).

## References
- https://github.com/py-pdf/pypdf/security/advisories/GHSA-4pxv-j86v-mhcw
- https://nvd.nist.gov/vuln/detail/CVE-2026-41313
- https://github.com/py-pdf/pypdf/pull/3735
- https://github.com/py-pdf/pypdf/commit/c50a0104cf083356f7c7f5d61410466a57f5c88a
- https://github.com/py-pdf/pypdf
- https://github.com/py-pdf/pypdf/releases/tag/6.10.2
