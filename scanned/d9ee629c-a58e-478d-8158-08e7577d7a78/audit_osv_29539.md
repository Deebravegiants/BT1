# [M] heap-buffer-overflow in ins_typebuf() in Vim < 9.1.0697

## Summary
Severity: Medium
Advisory: CVE-2024-43802
Aliases: GHSA-4ghr-c62x-cqfh
CVSS: 4.5 (CVSS:3.1/AV:L/AC:H/PR:N/UI:R/S:U/C:L/I:L/A:L)
Published: 2024-08-26
Source: https://osv.dev/vulnerability/CVE-2024-43802
Type: osv

## Details
Vim is an improved version of the unix vi text editor. When flushing the typeahead buffer, Vim moves the current position in the typeahead buffer but does not check whether there is enough space left in the buffer to handle the next characters.  So this may lead to the tb_off position within the typebuf variable to point outside of the valid buffer size, which can then later lead to a heap-buffer overflow in e.g. ins_typebuf(). Therefore, when flushing the typeahead buffer, check if there is enough space left before advancing the off position. If not, fall back to flush current typebuf contents. It's not quite clear yet, what can lead to this situation. It seems to happen when error messages occur (which will cause Vim to flush the typeahead buffer) in comnination with several long mappgins and so it may eventually move the off position out of a valid buffer size. Impact is low since it is not easily reproducible and requires to have several mappings active and run into some error condition. But when this happens, this will cause a crash. The issue has been fixed as of Vim patch v9.1.0697. Users are advised to upgrade. There are no known workarounds for this issue.

## References
- https://lists.debian.org/debian-lts-announce/2025/03/msg00023.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/43xxx/CVE-2024-43802.json
- https://github.com/vim/vim/security/advisories/GHSA-4ghr-c62x-cqfh
- https://nvd.nist.gov/vuln/detail/CVE-2024-43802
- https://security.netapp.com/advisory/ntap-20241004-0008/
- https://github.com/vim/vim/commit/322ba9108612bead5eb
