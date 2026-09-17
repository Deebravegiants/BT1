# [M] segmentation fault in win_line() in Vim < 9.1.1043

## Summary
Severity: Medium
Advisory: CVE-2025-24014
Aliases: GHSA-j3g9-wg22-v955
CVSS: 4.2 (CVSS:3.1/AV:L/AC:H/PR:L/UI:R/S:U/C:L/I:L/A:L)
Published: 2025-01-20
Source: https://osv.dev/vulnerability/CVE-2025-24014
Type: osv

## Details
Vim is an open source, command line text editor. A segmentation fault was found in Vim before 9.1.1043. In silent Ex mode (-s -e), Vim typically doesn't show a screen and just operates silently in batch mode. However, it is still possible to trigger the function that handles the scrolling of a gui version of Vim by feeding some binary characters to Vim. The function that handles the scrolling however may be triggering a redraw, which will access the ScreenLines pointer, even so this variable hasn't been allocated (since there is no screen). This vulnerability is fixed in 9.1.1043.

## References
- http://www.openwall.com/lists/oss-security/2025/01/20/4
- http://www.openwall.com/lists/oss-security/2025/01/21/1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/24xxx/CVE-2025-24014.json
- https://github.com/vim/vim/security/advisories/GHSA-j3g9-wg22-v955
- https://nvd.nist.gov/vuln/detail/CVE-2025-24014
- https://security.netapp.com/advisory/ntap-20250314-0005/
- https://github.com/vim/vim/commit/9d1bed5eccdbb46a26b8a484f5e9163c40e63919
