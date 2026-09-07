# [H] Kiwi TCMS Stored Cross-site Scripting via SVG file

## Summary
Severity: High
Advisory: GHSA-2wcr-87wf-cf9j
CVE: CVE-2023-27489
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:L (CVSS_V3)
Published: 2023-03-30
Source: https://github.com/advisories/GHSA-2wcr-87wf-cf9j
Type: github-advisory

## Affected
- PyPI: `kiwitcms` — affected >=0 <12.1

## Details
### Impact
Kiwi TCMS accepts SVG files uploaded by users which could potentially contain JavaScript code. If SVG images are viewed directly, i.e. not rendered in an HTML page, this JavaScript code could execute. 

### Patches
This vulnerability has been fixed by configuring Kiwi TCMS to serve with the Content-Security-Policy HTTP header which blocks inline JavaScript in all modern browsers.

### Workarounds
Configure Content-Security-Policy header, see [commit 6617cee0](https://github.com/kiwitcms/Kiwi/commit/6617cee0fb70cc394b7be6bbc86ef84e6e9de077).

### References
You can visit https://digi.ninja/blog/svg_xss.php for more technical details.

Independently disclosed by [Antonio Spataro](https://huntr.dev/bounties/bf99001b-a0a2-4f7d-98cd-983bc7f14a69/) and [@1d8](https://huntr.dev/bounties/f8c73bcc-02f3-4c65-a92b-1caa4d67c2fd/).

## References
- https://github.com/kiwitcms/Kiwi/security/advisories/GHSA-2wcr-87wf-cf9j
- https://nvd.nist.gov/vuln/detail/CVE-2023-27489
- https://github.com/kiwitcms/Kiwi/commit/6617cee0fb70cc394b7be6bbc86ef84e6e9de077
- https://github.com/kiwitcms/Kiwi
