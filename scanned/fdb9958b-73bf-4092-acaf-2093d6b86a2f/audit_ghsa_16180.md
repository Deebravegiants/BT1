# [H] HTML Cleaner allows crafted scripts in special contexts like svg or math to pass through

## Summary
Severity: High
Advisory: GHSA-5jfw-gq64-q45f
CVE: CVE-2024-52595
CWE: CWE-184, CWE-79, CWE-83
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:L/A:H (CVSS_V3)
Published: 2024-11-19
Source: https://github.com/advisories/GHSA-5jfw-gq64-q45f
Type: github-advisory

## Affected
- PyPI: `lxml-html-clean` — affected >=0 <0.4.0

## Details
### Impact

The HTML Parser in lxml does not properly handle context-switching for special HTML tags such as `<svg>`, `<math>` and `<noscript>`. This behavior deviates from how web browsers parse and interpret such tags. Specifically, content in CSS comments is ignored by lxml_html_clean but may be interpreted differently by web browsers, enabling malicious scripts to bypass the cleaning process. This vulnerability could lead to Cross-Site Scripting (XSS) attacks, compromising the security of users relying on lxml_html_clean in default configuration for sanitizing untrusted HTML content.

### Patches

Users employing the HTML cleaner in a security-sensitive context should upgrade to lxml 0.4.0, which addresses this issue.

### Workarounds

As a temporary mitigation, users can configure lxml_html_clean with the following settings to prevent the exploitation of this vulnerability:
* `remove_tags`: Specify tags to remove - their content is moved to their parents' tags.
* `kill_tags`: Specify tags to be removed completely.
* `allow_tags`: Restrict the set of permissible tags, excluding context-switching tags like `<svg>`, `<math>` and `<noscript>`.

### References

* https://github.com/fedora-python/lxml_html_clean/pull/19
* https://github.com/fedora-python/lxml_html_clean/pull/19/commits/c5d816f86eb3707d72a8ecf5f3823e0daa1b3808

## References
- https://github.com/fedora-python/lxml_html_clean/security/advisories/GHSA-5jfw-gq64-q45f
- https://nvd.nist.gov/vuln/detail/CVE-2024-52595
- https://github.com/fedora-python/lxml_html_clean/pull/19
- https://github.com/fedora-python/lxml_html_clean/commit/c5d816f86eb3707d72a8ecf5f3823e0daa1b3808
- https://github.com/fedora-python/lxml_html_clean
- https://github.com/pypa/advisory-database/tree/main/vulns/lxml-html-clean/PYSEC-2024-160.yaml
