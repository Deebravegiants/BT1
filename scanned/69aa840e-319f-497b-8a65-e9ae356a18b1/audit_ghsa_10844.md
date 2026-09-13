# [H] Sharp is Vulnerable to Path Traversal via Unsanitized Extension in FileUtil

## Summary
Severity: High
Advisory: GHSA-9ffq-6457-8958
CVE: CVE-2026-33686
CWE: CWE-22
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-03-25
Source: https://github.com/advisories/GHSA-9ffq-6457-8958
Type: github-advisory

## Affected
- Packagist: `code16/sharp` — affected >=0 <9.20.0

## Details
### Summary
A path traversal vulnerability exists in the FileUtil class of the code16/sharp package. The application fails to sanitize file extensions properly, allowing path separators to be passed into the storage layer.

### Detail
In `src/Utils/FileUtil.php`, the `FileUtil::explodeExtension()` function extracts a file's extension by splitting the filename at the last dot. However, the extracted extension is never sanitized. While the application uses a `normalizeName()` function, this function only cleans the base filename, meaning any path separators (such as /) injected into the extension will survive and be passed into the `storeAs()` function.

### Impact
Exploiting this flaw allows an authenticated attacker to manipulate file paths:
- Files can be written outside of the intended tmp directory via path traversal. For more details on the package, visit: https://github.com/code16/sharp
- Existing critical files (such as .env or configuration files) could potentially be overwritten. Review the CWE definition here: https://cwe.mitre.org/data/definitions/22.html (Note: This vulnerability was successfully chained with CWE-434 in a local Proof of Concept to confirm the traversal.)

### Patches
This issue has been patched by properly sanitizing the extension using `pathinfo(PATHINFO_EXTENSION)` instead of `strrpos()`, alongside applying strict regex replacements to both the base name and the extension. The fix is available in pull request #715

### Credits
Reported by [zaurgsynv](https://github.com/zaurgsynv).

## References
- https://github.com/code16/sharp/security/advisories/GHSA-9ffq-6457-8958
- https://nvd.nist.gov/vuln/detail/CVE-2026-33686
- https://github.com/code16/sharp/pull/715
- https://github.com/code16/sharp
