# [C] angular-base64-upload vulnerable to unauthenticated remote code execution

## Summary
Severity: Critical
Advisory: GHSA-vgxq-6rcf-qwrw
CVE: CVE-2024-42640
CWE: CWE-434
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2024-10-11
Source: https://github.com/advisories/GHSA-vgxq-6rcf-qwrw
Type: github-advisory

## Affected
- npm: `angular-base64-upload` — affected >=0 <0.1.21

## Details
angular-base64-upload versions prior to v0.1.21 are vulnerable to unauthenticated remote code execution via the `angular-base64-upload/demo/server.php` endpoint. Exploitation of this vulnerability involves uploading arbitrary file content to the server, which can subsequently accessed through the `angular-base64-upload/demo/uploads` endpoint. This leads to the execution of previously uploaded content which enables the attacker to achieve code execution on the server.

NOTE: This vulnerability only affects products that are no longer supported by the maintainer.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-42640
- https://github.com/adonespitogo/angular-base64-upload
- https://github.com/rvizx/CVE-2024-42640
- https://www.zyenra.com/blog/unauthenticated-rce-in-angular-base64-upload.html
