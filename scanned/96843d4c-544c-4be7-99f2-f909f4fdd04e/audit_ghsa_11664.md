# [H] Parse Server has a stored XSS filter bypass via Content-Type MIME parameter and missing XML extension blocklist entries

## Summary
Severity: High
Advisory: GHSA-42ph-pf9q-cr72
CVE: CVE-2026-32728
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:P/VC:H/VI:L/VA:N/SC:H/SI:L/SA:N (CVSS_V4)
Published: 2026-03-16
Source: https://github.com/advisories/GHSA-42ph-pf9q-cr72
Type: github-advisory

## Affected
- npm: `parse-server` — affected >=9.0.0 <9.6.0-alpha.15
- npm: `parse-server` — affected >=0 <8.6.41

## Details
### Impact

An attacker who is allowed to upload files can bypass the file extension filter by appending a MIME parameter (e.g. `;charset=utf-8`) to the `Content-Type` header. This causes the extension validation to fail matching against the blocklist, allowing active content to be stored and served under the application's domain. In addition, certain XML-based file extensions that can render scripts in web browsers are not included in the default blocklist.

This can lead to stored XSS attacks, compromising session tokens, user credentials, or other sensitive data accessible via the browser's local storage.

### Patches

The fix strips MIME parameters from the `Content-Type` header before validating the file extension against the blocklist. The default blocklist has also been extended to include additional XML-based extensions (`xsd`, `rng`, `rdf`, `rdf+xml`, `owl`, `mathml`, `mathml+xml`) that can render active content in web browsers.

Note that the `fileUpload.fileExtensions` option is intended to be configured as an allowlist of file extensions that are valid for a specific application, not as a denylist. The default denylist is provided only as a basic default that covers most common problematic extensions. It is not intended to be an exhaustive list of all potentially dangerous extensions. Developers should not rely on the default value, as new extensions that can render active content in browsers might emerge in the future.

### Workarounds

Configure the `fileUpload.fileExtensions` option to use an allowlist of only the file extensions that your application needs, rather than relying on the default blocklist.

## References
- https://github.com/parse-community/parse-server/security/advisories/GHSA-42ph-pf9q-cr72
- https://nvd.nist.gov/vuln/detail/CVE-2026-32728
- https://github.com/parse-community/parse-server/pull/10191
- https://github.com/parse-community/parse-server/pull/10192
- https://github.com/parse-community/parse-server/commit/4f53ab3cad5502a51a509d53f999e00ff7217b8d
- https://github.com/parse-community/parse-server/commit/c7599c577a02b97eb5e76d4e20517b0283ae73c8
- https://github.com/parse-community/parse-server
