# [M] Formwork CMS has Stored Cross-Site Scripting Vulnerebility in Blog Tags

## Summary
Severity: Medium
Advisory: GHSA-7j46-f57w-76pj
CVE: CVE-2025-65956
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:L (CVSS_V3)
Published: 2025-11-24
Source: https://github.com/advisories/GHSA-7j46-f57w-76pj
Type: github-advisory

## Affected
- Packagist: `getformwork/formwork` — affected >=0 <2.2.0

## Details
### Summary
Inserting unsanitized data into the blog tag field in Formwork CMS results in stored cross‑site scripting (XSS).
Any user with credentials to the Formwork CMS who accesses or edits an affected blog post will have attacker‑controlled script executed in their browser. Because the issue is persistent and impacts privileged administrative workflows, the severity is elevated.

### Details
Formwork CMS fails to properly sanitize data inserted into tags, before saving them and rendering them into the edit blog interface.  When a specially crafted tag becomes saved as a tag into the system, it is unable to be removed.  Any attempt to remove the tag from the affected post, causes the XSS to trigger once again.

Additionally, once the malicious tag is present, managing standard tags becomes impossible. This is due to script execution on attempted modification. This leads to a form of interface lockout where the payload continually reinserts itself due to the stored, unsafe rendering.

### Impact
This is a stored cross‑site scripting (XSS) vulnerability.

This impacts all users who access the affected blog post’s edit page.

### Patches
[Formwork 2.2.0](https://github.com/getformwork/formwork/releases/tag/2.2.0) ensures proper escaping of user input in tag fields.

## References
- https://github.com/getformwork/formwork/security/advisories/GHSA-7j46-f57w-76pj
- https://nvd.nist.gov/vuln/detail/CVE-2025-65956
- https://github.com/getformwork/formwork/pull/791
- https://github.com/getformwork/formwork/commit/4abcd60ae7692b46d316f956b0b20fb85336f3b2
- https://github.com/getformwork/formwork
