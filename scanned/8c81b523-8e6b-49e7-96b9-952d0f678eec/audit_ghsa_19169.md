# [H] Connect-CMS information that is restricted to viewing is visible

## Summary
Severity: High
Advisory: GHSA-2237-5r9w-vm8j
CWE: CWE-200
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-02-07
Source: https://github.com/advisories/GHSA-2237-5r9w-vm8j
Type: github-advisory

## Affected
- Packagist: `opensource-workshop/connect-cms` — affected >=0 <1.8.4

## Details
### Impact
 - Information that is restricted from viewing in the search results of site searches (※) can still be viewed via the main text (a feature added in v1.8.0).
     - Impact by version
         - v1.8.0 ~ v1.8.3: It will be displayed in the text.
         - v1.8.0 and earlier: It will not be displayed in the body of the text, but the title (frame name) will be displayed with a link.
     - Target viewing restriction function
         - Frame publishing function (private, limited publishing)
         - IP Restriction Page
         - Password setting page

### Patches (fixed version)
 - Apply v1.8.4.

### Workarounds
 - Remove the site search (e.g. hide frames).。

### References
none

## References
- https://github.com/opensource-workshop/connect-cms/security/advisories/GHSA-2237-5r9w-vm8j
- https://github.com/opensource-workshop/connect-cms
