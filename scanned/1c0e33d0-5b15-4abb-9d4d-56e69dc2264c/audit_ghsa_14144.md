# [M] Phishing attack vulnerability by uploading malicious HTML file

## Summary
Severity: Medium
Advisory: GHSA-9prm-jqwx-45x9
CVE: CVE-2023-32689
CWE: CWE-434
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2023-05-31
Source: https://github.com/advisories/GHSA-9prm-jqwx-45x9
Type: github-advisory

## Affected
- npm: `parse-server` — affected >=0 <5.4.4
- npm: `parse-server` — affected >=6.0.0 <6.1.1

## Details
### Impact

Phishing attack vulnerability by uploading malicious files. A malicious user could upload a HTML file to Parse Server via its public API. That HTML file would then be accessible at the internet domain at which Parse Server is hosted. The URL of the the uploaded HTML could be shared for phishing attacks. The HTML page may seem legitimate because it is served under the internet domain where Parse Server is hosted, which may be the same as a company's official website domain.

An additional security issue arises when the Parse JavaScript SDK is used. The SDK stores sessions in the internet browser's local storage, which usually restricts data access depending on the internet domain. A malicious HTML file could contain a script that retrieves the user's session token from local storage and then share it with the attacker.

### Patches

The fix adds a new Parse Server option `fileUpload.fileExtensions` to restrict file upload on Parse Server by file extension. It is recommended to restrict file upload for HTML file extensions, which this fix disables by default. If an app requires upload of files with HTML file extensions, the option can be set to `['.*']` or another custom value to override the default.

### References

- https://github.com/parse-community/parse-server/security/advisories/GHSA-9prm-jqwx-45x9
- https://github.com/parse-community/parse-server/pull/8538 (Parse Server 6)
- https://github.com/parse-community/parse-server/pull/8537 (Parse Server 5)

## References
- https://github.com/parse-community/parse-server/security/advisories/GHSA-9prm-jqwx-45x9
- https://nvd.nist.gov/vuln/detail/CVE-2023-32689
- https://github.com/parse-community/parse-server/pull/8537
- https://github.com/parse-community/parse-server/pull/8538
- https://github.com/parse-community/parse-server
