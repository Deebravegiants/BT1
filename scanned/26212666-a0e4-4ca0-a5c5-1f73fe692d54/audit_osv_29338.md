# [M] Vim < v9.1.0648 has a double-free in dialog_changed()

## Summary
Severity: Medium
Advisory: CVE-2024-41965
Aliases: GHSA-46pw-v7qw-xc2f
CVSS: 4.2 (CVSS:3.1/AV:L/AC:H/PR:L/UI:R/S:U/C:L/I:L/A:L)
Published: 2024-08-01
Source: https://osv.dev/vulnerability/CVE-2024-41965
Type: osv

## Details
Vim is an open source command line text editor. double-free in dialog_changed() in Vim < v9.1.0648. When abandoning a buffer, Vim may ask the user what to do with the modified buffer. If the user wants the changed buffer to be saved, Vim may create a new Untitled file, if the buffer did not have a name yet. However, when setting the buffer name to Unnamed, Vim will falsely free a pointer twice, leading to a double-free and possibly later to a heap-use-after-free, which can lead to a crash. The issue has been fixed as of Vim patch v9.1.0648.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/41xxx/CVE-2024-41965.json
- https://github.com/vim/vim/security/advisories/GHSA-46pw-v7qw-xc2f
- https://nvd.nist.gov/vuln/detail/CVE-2024-41965
- https://security.netapp.com/advisory/ntap-20241115-0002/
- https://github.com/vim/vim/commit/b29f4abcd4b3382fa746edd1d0562b7b48c
