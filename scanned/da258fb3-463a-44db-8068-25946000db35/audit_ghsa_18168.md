# [M] jsondiffpatch is vulnerable to Cross-site Scripting (XSS) via HtmlFormatter::nodeBegin

## Summary
Severity: Medium
Advisory: GHSA-33vc-wfww-vjfv
CVE: CVE-2025-9910
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2025-09-11
Source: https://github.com/advisories/GHSA-33vc-wfww-vjfv
Type: github-advisory

## Affected
- npm: `jsondiffpatch` — affected >=0 <0.7.2

## Details
### Vulnerability in jsondiffpatch

Versions of `jsondiffpatch` prior to `0.7.2` are vulnerable to Cross-site Scripting (XSS) in the `HtmlFormatter` (`HtmlFormatter::nodeBegin`). When diffs are rendered to HTML using the built-in formatter, untrusted payloads can inject scripts and execute in the context of a consuming web page.

**Affected versions:** >= 0, < 0.7.2
**Patched version:** 0.7.2

**Remediation**
Upgrade to `jsondiffpatch` `0.7.2` or later. The fix hardens the HTML formatter to avoid script injection.

**Workarounds**
Avoid using the HTML formatter on untrusted diffs, or sanitize/escape the rendered output.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-9910
- https://github.com/benjamine/jsondiffpatch/issues/383
- https://github.com/benjamine/jsondiffpatch/commit/0e374b5dd8d7879b329a9fc18affbd46ad50dd14
- https://benjamine.github.io/jsondiffpatch/index.html
- https://github.com/benjamine/jsondiffpatch
- https://security.snyk.io/vuln/SNYK-JAVA-ORGWEBJARSBOWER-12549277
- https://security.snyk.io/vuln/SNYK-JAVA-ORGWEBJARSNPM-12549276
- https://security.snyk.io/vuln/SNYK-JS-JSONDIFFPATCH-10369031
