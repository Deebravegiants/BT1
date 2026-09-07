# [H] XBlock vulnerable to Cross-Site Scripting (XSS) 

## Summary
Severity: High
Advisory: GHSA-qv6c-367r-3w6q
CVE: CVE-2022-46147
CWE: CWE-79, CWE-80
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2022-12-02
Source: https://github.com/advisories/GHSA-qv6c-367r-3w6q
Type: github-advisory

## Affected
- PyPI: `xblock-drag-and-drop-v2` — affected >=0 <3.0.0

## Details
### Impact
XSS Vulnerability in multiple XBlock Fields.  Any platform that has deployed the XBlock will be impacted.

### Patches
https://github.com/openedx/xblock-drag-and-drop-v2/commit/53c4482f9bb6d8c7ccdf5253bd82c84a222b2492

The fix is compatible with all Open edX releases newer than Lilac.

### Workarounds
None.

### References
https://github.com/openedx/xblock-drag-and-drop-v2/pull/295#issuecomment-1277693864

## References
- https://github.com/openedx/xblock-drag-and-drop-v2/security/advisories/GHSA-qv6c-367r-3w6q
- https://nvd.nist.gov/vuln/detail/CVE-2022-46147
- https://github.com/openedx/xblock-drag-and-drop-v2/pull/295#issuecomment-1277693864
- https://github.com/openedx/xblock-drag-and-drop-v2/commit/53c4482f9bb6d8c7ccdf5253bd82c84a222b2492
- https://github.com/openedx/xblock-drag-and-drop-v2/commit/68887d1b4a44325d2de7573d450e41129ba98b1a
- https://github.com/openedx/xblock-drag-and-drop-v2
- https://github.com/openedx/xblock-drag-and-drop-v2/releases/tag/v3.0.0
- https://github.com/pypa/advisory-database/tree/main/vulns/xblock-drag-and-drop-v2/PYSEC-2022-43175.yaml
