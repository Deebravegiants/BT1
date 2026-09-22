# [H] CVE-2020-15236

## Summary
Severity: High
Advisory: CVE-2020-15236
Aliases: GHSA-whpv-5xg2-w527
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2020-10-05
Source: https://osv.dev/vulnerability/CVE-2020-15236
Type: osv

## Details
In Wiki.js before version 2.5.151, directory traversal outside of Wiki.js context is possible when a storage module with local asset cache fetching is enabled. A malicious user can potentially read any file on the file system by crafting a special URL that allows for directory traversal. This is only possible when a storage module implementing local asset cache (e.g Local File System or Git) is enabled and that no web application firewall solution (e.g. cloudflare) strips potentially malicious URLs. Commit 084dcd69d1591586ee4752101e675d5f0ac6dcdc fixes this vulnerability by sanitizing the path before it is passed on to the storage module. The sanitization step removes any directory traversal (e.g. `..` and `.`) sequences as well as invalid filesystem characters from the path. As a workaround, disable any storage module with local asset caching capabilities such as Local File System and Git.

## References
- https://github.com/Requarks/wiki/security/advisories/GHSA-whpv-5xg2-w527
- https://github.com/Requarks/wiki/commit/084dcd69d1591586ee4752101e675d5f0ac6dcdc
