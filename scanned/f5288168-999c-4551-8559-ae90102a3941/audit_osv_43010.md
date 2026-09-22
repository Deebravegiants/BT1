# [C] cifs: validate DFS referral string offsets

## Summary
Severity: Critical
Advisory: CVE-2026-72318
Ecosystem: Linux
CVSS: 9.4 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72318
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.11.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

cifs: validate DFS referral string offsets

parse_dfs_referrals() validates that the response header and referral
array fit in the received buffer, but each referral also contains string
offsets supplied by the server.

Those offsets are used to compute the DfsPath and NetworkAddress string
pointers without checking whether they still point inside the response
buffer. A malformed referral can therefore make the computed pointer
exceed the end of the buffer. The resulting negative max_len is then
passed to cifs_strndup_from_utf16(), and the non-Unicode path forwards it
to kstrndup() as a size_t, allowing strnlen() to read out of bounds.

Validate each string offset before deriving the string pointer.

## References
- https://git.kernel.org/stable/c/027a84ac6b50c12ef767c15abfc58aa865820e9e
- https://git.kernel.org/stable/c/76c607b9353d377b1d1b11db50e743eee0ccf658
- https://git.kernel.org/stable/c/929a85932d14190988f1eafd6ee8cc68d66ace0b
- https://git.kernel.org/stable/c/b784cd1c24d89bf71be2efe1e948ff7c03371e57
- https://git.kernel.org/stable/c/c37abc99bb3de3d3219ecef253d649f74117fd83
- https://git.kernel.org/stable/c/d64b6be5740ce230aca184d8d224c75d9866045d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72318.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72318
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
