# [M] ZIP64 End of Central Directory (EOCD) Locator record offset not checked

## Summary
Severity: Medium
Advisory: BIT-libpython-2025-8291
Aliases: BIT-python-2025-8291, BIT-python-min-2025-8291, CVE-2025-8291, GHSA-hhv7-p4pg-wm6p, PSF-2025-12
Ecosystem: Bitnami
Published: 2025-10-14
Source: https://osv.dev/vulnerability/BIT-libpython-2025-8291
Type: osv

## Affected
- Bitnami: `libpython` — affected >=3.14.0 <3.14.1

## Details
The 'zipfile' module would not check the validity of the ZIP64 End of
Central Directory (EOCD) Locator record offset value would not be used to
locate the ZIP64 EOCD record, instead the ZIP64 EOCD record would be
assumed to be the previous record in the ZIP archive. This could be abused
to create ZIP archives that are handled differently by the 'zipfile' module
compared to other ZIP implementations.


Remediation maintains this behavior, but checks that the offset specified
in the ZIP64 EOCD Locator record matches the expected value.

## References
- https://github.com/python/cpython/commit/162997bb70e067668c039700141770687bc8f267
- https://github.com/python/cpython/commit/1d29afb0d6218aa8fb5e1e4a6133a4778d89bb46
- https://github.com/python/cpython/commit/333d4a6f4967d3ace91492a39ededbcf3faa76a6
- https://github.com/python/cpython/commit/76437ac248ad8ca44e9bf697b02b1e2241df2196
- https://github.com/python/cpython/commit/8392b2f0d35678407d9ce7d95655a5b77de161b4
- https://github.com/python/cpython/commit/bca11ae7d575d87ed93f5dd6a313be6246e3e388
- https://github.com/python/cpython/commit/d11e69d6203080e3ec450446bfed0516727b85c3
- https://github.com/python/cpython/issues/139700
- https://github.com/python/cpython/pull/139702
- https://mail.python.org/archives/list/security-announce@python.org/thread/QECOPWMTH4VPPJAXAH2BGTA4XADOP62G/
- https://nvd.nist.gov/vuln/detail/CVE-2025-8291
- https://github.com/google/security-research/security/advisories/GHSA-hhv7-p4pg-wm6p
- https://github.com/psf/advisory-database/blob/main/advisories/python/PSF-2025-12.json
