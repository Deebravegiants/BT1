# [M] XSS in Flarum Sticky extension

## Summary
Severity: Medium
Advisory: GHSA-h3gg-7wx2-cq3h
CVE: CVE-2021-21283
CWE: CWE-79
Ecosystem: Packagist
Published: 2021-01-29
Source: https://github.com/advisories/GHSA-h3gg-7wx2-cq3h
Type: github-advisory

## Affected
- Packagist: `flarum/sticky` — affected >=0.1.0-beta.14 <0.1.0-beta.15.1

## Details
### Impact
A change in release beta 14 of the Sticky extension caused the plain text content of the first post of a pinned discussion to be injected as HTML on the discussion list. The issue was discovered following an internal audit.

Any HTML would be injected through Mithril's `m.trust()` helper. This resulted in an HTML injection where `<script>` tags would not be executed. However it was possible to run javascript from other HTML attributes, enabling a cross-site scripting (XSS) attack to be performed.

Since the exploit only happens with the first post of a pinned discussion, an attacker would need the ability to pin their own discussion, or be able to edit a discussion that was previously pinned.

On forums where all pinned posts are authored by your staff, you can be relatively certain the vulnerability has not been exploited.

Forums where some user-created discussions were pinned can look at the first post edit date to find whether the vulnerability might have been exploited. Because Flarum doesn't store the post content history, you cannot be certain if a malicious edit was reverted.

### Patches
The fix will be available in version v0.1.0-beta.16 with Flarum beta 16. The fix has already been back-ported to Flarum beta 15 as version v0.1.0-beta.15.1 of the Sticky extension.

### Workarounds
Forum administrators can disable the Sticky extension until they are able to apply the update. The vulnerability cannot be exploited while the extension is disabled.

### References

- [Release announcement](https://discuss.flarum.org/d/26042-security-update-to-flarum-sticky-010-beta151)
- [Pull Request](https://github.com/flarum/sticky/pull/24)

### For more information
If you have any questions or comments about this advisory, please start a new discussion on our [support forum](https://discuss.flarum.org/t/support).

If you discover a security vulnerability within Flarum, please send an e-mail to [security@flarum.org](mailto:security@flarum.org). All security vulnerabilities will be promptly addressed. More details can be found in our [security policy](https://github.com/flarum/core/security/policy).

## References
- https://github.com/flarum/sticky/security/advisories/GHSA-h3gg-7wx2-cq3h
- https://nvd.nist.gov/vuln/detail/CVE-2021-21283
- https://github.com/flarum/sticky/pull/24
- https://github.com/flarum/sticky/commit/7ebd30462bd405c4c0570b93a6d48710e6c3db19
- https://discuss.flarum.org/d/26042-security-update-to-flarum-sticky-010-beta151)
