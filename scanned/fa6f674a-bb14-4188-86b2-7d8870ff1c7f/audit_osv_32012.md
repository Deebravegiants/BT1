# [M] heap-buffer-overflow with visual mode in Vim < 9.1.1003

## Summary
Severity: Medium
Advisory: CVE-2025-22134
Aliases: GHSA-5rgf-26wj-48v8
CVSS: 4.2 (CVSS:3.1/AV:L/AC:H/PR:L/UI:R/S:U/C:L/I:L/A:L)
Published: 2025-01-13
Source: https://osv.dev/vulnerability/CVE-2025-22134
Type: osv

## Details
When switching to other buffers using the :all command and visual mode still being active, this may cause a heap-buffer overflow, because Vim does not properly end visual mode and therefore may try to access beyond the end of a line in a buffer. In Patch 9.1.1003 Vim will correctly reset the visual mode before opening other windows and buffers and therefore fix this bug. In addition it does verify that it won't try to access a position if the position is greater than the corresponding buffer line. Impact is medium since the user must have switched on visual mode when executing the :all ex command. The Vim project would like to thank github user gandalf4a for reporting this issue. The issue has been fixed as of Vim patch v9.1.1003

## References
- http://www.openwall.com/lists/oss-security/2025/01/11/1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/22xxx/CVE-2025-22134.json
- https://github.com/vim/vim/security/advisories/GHSA-5rgf-26wj-48v8
- https://nvd.nist.gov/vuln/detail/CVE-2025-22134
- https://security.netapp.com/advisory/ntap-20250314-0004/
- https://github.com/vim/vim/commit/c9a1e257f1630a0866447e53a564f7ff96a80ead
