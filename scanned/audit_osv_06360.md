# [M] tarfile.data_filter path traversal bypass allows writing outside the extraction directory

## Summary
Severity: Medium
Advisory: BIT-libpython-2026-7774
Aliases: BIT-python-2026-7774, BIT-python-min-2026-7774, CVE-2026-7774, PSF-2026-26
Ecosystem: Bitnami
Published: 2026-06-08
Source: https://osv.dev/vulnerability/BIT-libpython-2026-7774
Type: osv

## Affected
- Bitnami: `libpython` — affected >=3.14.0 <3.14.6

## Details
tarfile.data_filter could be bypassed using crafted link entries, including symlinks with empty or directory-like names, to redirect later archive members outside the intended extraction directory. This allowed a malicious tar archive to cause tarfile.extractall() to write files outside the destination directory, subject to the permissions of the extracting process.

## References
- http://www.openwall.com/lists/oss-security/2026/06/04/9
- https://github.com/python/cpython/issues/149486
- https://github.com/python/cpython/pull/149487
- https://mail.python.org/archives/list/security-announce@python.org/thread/4FU62L2M6RMMHT2QPGQNPEHHUND7CEX5/
- https://nvd.nist.gov/vuln/detail/CVE-2026-7774
- https://github.com/python/cpython/commit/0478bd83d82b255e0f29f613367a59d261e7eaa2
- https://github.com/python/cpython/commit/0d28f5e46e151718972dfabd91205444d0037b6d
- https://github.com/python/cpython/commit/578411982c16f753f4893532510099ef665117da
- https://github.com/python/cpython/commit/5cf47a248c35c375d610b87b2f72fd1ed454b558
- https://github.com/python/cpython/commit/74cca9a92fb7d653e404843a56b8bdc7b0afdbbf
- https://github.com/python/cpython/commit/10a13bee3c24f9c62b602e696334ff2272a40efc
- https://github.com/python/cpython/commit/c063191cb7f9170f9565e305f8aa2b79ab2bf609
