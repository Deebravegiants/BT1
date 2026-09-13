# [M] heap-buffer-overflow in do_search() in Vim < 9.1.0689

## Summary
Severity: Medium
Advisory: CVE-2024-43790
Aliases: GHSA-v2x2-cjcg-f9jm
CVSS: 4.5 (CVSS:3.1/AV:L/AC:H/PR:N/UI:R/S:U/C:L/I:L/A:L)
Published: 2024-08-22
Source: https://osv.dev/vulnerability/CVE-2024-43790
Type: osv

## Details
Vim is an open source command line text editor. When performing a search and displaying the search-count message is disabled (:set shm+=S), the search pattern is displayed at the bottom of the screen in a buffer (msgbuf). When right-left mode (:set rl) is enabled, the search pattern is reversed. This happens by allocating a new buffer. If the search pattern contains some ASCII NUL characters, the buffer allocated will be smaller than the original allocated buffer (because for allocating the reversed buffer, the strlen() function is called, which only counts until it notices an ASCII NUL byte ) and thus the original length indicator is wrong. This causes an overflow when accessing characters inside the msgbuf by the previously (now wrong) length of the msgbuf. The issue has been fixed as of Vim patch v9.1.0689.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/43xxx/CVE-2024-43790.json
- https://github.com/vim/vim/security/advisories/GHSA-v2x2-cjcg-f9jm
- https://nvd.nist.gov/vuln/detail/CVE-2024-43790
- https://security.netapp.com/advisory/ntap-20240920-0005/
- https://github.com/vim/vim/commit/cacb6693c10bb19f28a50eca47bc
