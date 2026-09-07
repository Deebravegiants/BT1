# [M] OpenList (frontend) allows XSS Attacks in the built-in Markdown Viewer

## Summary
Severity: Medium
Advisory: GHSA-2hw3-h8qx-hqqp
CVE: CVE-2025-50183
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2025-06-18
Source: https://github.com/advisories/GHSA-2hw3-h8qx-hqqp
Type: github-advisory

## Affected
- npm: `@openlist-frontend/openlist-frontend` — affected >=0 <4.0.0-rc.4

## Details
XSS via `.py` file containing script tag interpreted as HTML

## Summary

A vulnerability exists in the file preview/browsing feature of the application, where files with a `.py` extension that contain JavaScript code wrapped in `<script>` tags may be interpreted and executed as HTML in certain modes. This leads to a stored XSS vulnerability.

## Affected Versions

* <= 4.0.0-rc.3

## PoC

Create a `.py` file with arbitrary JavaScript content wrapped in `<script>` tags. For example:

```javascript
<script>alert(document.cookie);</script>
```

When a victim views the file in browsing mode (e.g., a rendered preview), the JavaScript is executed in the browser context.

--- 

## Attack vector

An attacker can place such a `.py` file in the system via remote channels, such as:
* Convincing a webmaster to download or upload the file; 
* Tricking users into accessing a file link via public URLs.

## Required permissions

* None, if public or visitor access is enabled.
* If the file is uploaded by a user with elevated permissions, potential privilege boundaries may be crossed.

## User interaction

Yes. The user must manually click to switch to the browsing or preview mode to trigger the script. And seems only when using `ISO-8859-1` encoding.

## Scope

* Unchanged `(S:U)` - The attack does not cross system or privilege boundaries in general.
* ⚠️ Controversial edge case: If sensitive preview files are accessible due to misconfiguration, scope could be considered Changed `(S:C)`.

## Impact

* Confidentiality: User information including cookies, login state, and localStorage may be accessed. Some files that only can be viewed via this user will leak too.
* Integrity & Availability: Not directly impacted.

---

## Recommendations

* Treat all previewed file types (including non-HTML like .py) as plain text unless explicitly sanitized.
* Disable rendering modes that can interpret user-uploaded content as HTML.

## Timeline

| Date | Event |
|------|-------|
| 2025-06-17 | Vulnerability reported |
| 2025-06-17 | Comminuty Manager confirmed |
| 2025-06-17 | Fixed |

# Credits

* Discovered by: @zyk2507
* Reported to: [The OpenList Team](https://github.com/OpenListTeam)
* Analyzed and confirmed by: @jyxjjj
* Fixed by: @cxw620
* Fixed in: `4.0.0-rc.4`

## References
- https://github.com/OpenListTeam/OpenList/security/advisories/GHSA-2hw3-h8qx-hqqp
- https://nvd.nist.gov/vuln/detail/CVE-2025-50183
- https://github.com/OpenListTeam/OpenList-Frontend/commit/7b5ed20c608c7b9b36d1950a386678e0a89f8175
- https://github.com/OpenListTeam/OpenList
