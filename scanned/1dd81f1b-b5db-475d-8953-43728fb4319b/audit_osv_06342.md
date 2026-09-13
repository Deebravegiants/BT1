# [H] tarfile extraction filter bypass allows escaping the destination directory

## Summary
Severity: High
Advisory: BIT-libpython-2026-11940
Aliases: BIT-python-2026-11940, BIT-python-min-2026-11940, CVE-2026-11940, PSF-2026-30
Ecosystem: Bitnami
Published: 2026-07-30
Source: https://osv.dev/vulnerability/BIT-libpython-2026-11940
Type: osv

## Affected
- Bitnami: `libpython` — affected >=3.14.0 <3.14.7

## Details
tarfile.extractall() with the 'data' or 'tar'
 filter could be bypassed by a crafted archive where a hardlink 
references a symlink stored at a deeper name than the hardlink itself.  
The extraction fallback validated the symlink at it's archived location 
but recreated it at the hardlink's shallower
path, letting a relative
 target the filter judged contained escape the destination directory.  
This allowed a malicious tar archive to create a symlink pointing 
outside the destination, enabling out-of-destination file reads or 
writes. This was an incomplete fix of CVE-2025-4330.

## References
- https://github.com/python/cpython/commit/27dd970bf6b17ebca7c8ed486a40ab043ed7af8f
- https://github.com/python/cpython/commit/672825e2f36a57e173959b0d9d409d4560dab8df
- https://github.com/python/cpython/commit/771d12dda5140313db0ac550292987975651bbde
- https://github.com/python/cpython/commit/79c06bd5c6afa3c440d50faf7ee1b147c8832b4c
- https://github.com/python/cpython/commit/be13e86f6b9788a6f4d0419dffef72cbae5865c9
- https://github.com/python/cpython/issues/151558
- https://github.com/python/cpython/pull/151559
- https://mail.python.org/archives/list/security-announce@python.org/thread/LD6QIISNQFQYOIEPJNEUIPV7S3V76FZH/
- https://nvd.nist.gov/vuln/detail/CVE-2026-11940
- https://github.com/python/cpython/commit/0f852b3f07dd8e71e40326a51c02afbf16a42cc5
- https://github.com/python/cpython/commit/e5fdbd8d5aa923bd9111b112ea73bd6ec7c47877
