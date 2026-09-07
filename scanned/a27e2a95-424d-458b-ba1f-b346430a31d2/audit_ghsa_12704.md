# [H] Livebook Desktop's protocol handler can be exploited to execute arbitrary command on Windows

## Summary
Severity: High
Advisory: GHSA-564w-97r7-c6p9
CVE: CVE-2023-35174
CWE: CWE-78
Ecosystem: Hex
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:H/A:L (CVSS_V3)
Published: 2023-06-21
Source: https://github.com/advisories/GHSA-564w-97r7-c6p9
Type: github-advisory

## Affected
- Hex: `livebook` — affected >=0.8.0 <0.8.2
- Hex: `livebook` — affected >=0.9.0 <0.9.3

## Details
On Windows, it is possible to open a `livebook://` link from a browser which opens Livebook Desktop and triggers arbitrary code execution on victim's machine.

Any user using Livebook Desktop on Windows is potentially vulnerable to arbitrary code execution when they expect Livebook to be opened from browser.

## References
- https://github.com/livebook-dev/livebook/security/advisories/GHSA-564w-97r7-c6p9
- https://nvd.nist.gov/vuln/detail/CVE-2023-35174
- https://github.com/livebook-dev/livebook/commit/2e11b59f677c6ed3b6aa82dad412a8b3406ffdf1
- https://github.com/livebook-dev/livebook/commit/beb10daaadcc765f0380e436bd7cd5f74cf086c8
- https://github.com/livebook-dev/livebook
- https://github.com/livebook-dev/livebook/releases/tag/v0.8.2
- https://github.com/livebook-dev/livebook/releases/tag/v0.9.3
