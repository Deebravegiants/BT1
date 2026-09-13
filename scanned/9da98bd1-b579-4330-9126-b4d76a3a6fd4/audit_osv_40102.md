# [M] CVE-2026-4983

## Summary
Severity: Medium
Advisory: CVE-2026-4983
CVSS: 4.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:N/I:L/A:N)
Published: 2026-06-23
Source: https://osv.dev/vulnerability/CVE-2026-4983
Type: osv

## Details
Open VSX Registry does not sanitize SVG files uploaded as extension icons prior to storage, and serves them with Content-Type: image/svg+xml without security headers such as Content-Security-Policy or Content-Disposition: attachment. This allows an attacker to publish an extension with a malicious SVG icon and achieve stored cross-site scripting (XSS) when a user navigates directly to the icon URL.




On deployments using local storage, script execution occurs within the Open VSX application origin, enabling session hijacking, authentication token theft, and unauthorized extension publishing. On deployments backed by external storage (such as open-vsx.org with an S3-backed CDN), execution is confined to the storage origin, reducing impact but still permitting phishing attacks and credential harvesting through attacker-crafted pages.

## References
- https://gitlab.eclipse.org/security/cve-assignment/-/work_items/91
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/4xxx/CVE-2026-4983.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-4983
- https://github.com/eclipse-openvsx/openvsx
