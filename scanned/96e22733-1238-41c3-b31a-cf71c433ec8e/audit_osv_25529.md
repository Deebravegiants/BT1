# [H] Tolgee Lacks Permission Check for API Key for some endpoints

## Summary
Severity: High
Advisory: CVE-2023-38510
Aliases: GHSA-4f9j-4vh4-p85v
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2023-07-27
Source: https://osv.dev/vulnerability/CVE-2023-38510
Type: osv

## Details
Tolgee is an open-source localization platform. Starting in version 3.14.0 and prior to version 3.23.1, when a request is made using an API key, the backend fails to verify the permission scopes associated with the key, effectively bypassing permission checks entirely for some endpoints. It's important to note that this vulnerability only affects projects that have inadvertently exposed their API keys on the internet. Projects that have kept their API keys secure are not impacted. This issue is fixed in version 3.23.1.

## References
- https://github.com/tolgee/tolgee-platform/releases/tag/v3.23.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/38xxx/CVE-2023-38510.json
- https://github.com/tolgee/tolgee-platform/security/advisories/GHSA-4f9j-4vh4-p85v
- https://nvd.nist.gov/vuln/detail/CVE-2023-38510
- https://github.com/tolgee/tolgee-platform/commit/4776cba67e7bb8c1b0259376e3e5fa3bb46e45c7
- https://github.com/tolgee/tolgee-platform/pull/1818
