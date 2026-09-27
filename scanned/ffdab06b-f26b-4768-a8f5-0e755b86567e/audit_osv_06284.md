# [C] BIT-libpython-2020-27619

## Summary
Severity: Critical
Advisory: BIT-libpython-2020-27619
Aliases: BIT-python-2020-27619, BIT-python-min-2020-27619, CVE-2020-27619, PSF-2020-6
Ecosystem: Bitnami
Published: 2025-08-11
Source: https://osv.dev/vulnerability/BIT-libpython-2020-27619
Type: osv

## Affected
- Bitnami: `libpython` — affected >=3.9.0 <3.9.1

## Details
In Python 3 through 3.9.0, the Lib/test/multibytecodec_support.py CJK codec tests call eval() on content retrieved via HTTP.

## References
- https://bugs.python.org/issue41944
- https://github.com/python/cpython/commit/2ef5caa58febc8968e670e39e3d37cf8eef3cab8
- https://github.com/python/cpython/commit/43e523103886af66d6c27cd72431b5d9d14cd2a9
- https://github.com/python/cpython/commit/6c6c256df3636ff6f6136820afaefa5a10a3ac33
- https://github.com/python/cpython/commit/b664a1df4ee71d3760ab937653b10997081b1794
- https://github.com/python/cpython/commit/e912e945f2960029d039d3390ea08835ad39374b
- https://lists.apache.org/thread.html/r58af02e294bd07f487e2c64ffc0a29b837db5600e33b6e698b9d696b%40%3Cissues.bookkeeper.apache.org%3E
- https://lists.apache.org/thread.html/rf4c02775860db415b4955778a131c2795223f61cb8c6a450893651e4%40%3Cissues.bookkeeper.apache.org%3E
- https://lists.apache.org/thread.html/rf9fa47ab66495c78bb4120b0754dd9531ca2ff0430f6685ac9b07772%40%3Cdev.mina.apache.org%3E
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/RSLQD5CCM75IZGAMBDGUZEATYU5YSGJ7/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/SGIY6I4YS3WOXAK4SXKIEOC2G4VZKIR7/
- https://nvd.nist.gov/vuln/detail/CVE-2020-27619
- https://security.gentoo.org/glsa/202402-04
- https://security.netapp.com/advisory/ntap-20201123-0004/
- https://www.oracle.com/security-alerts/cpujul2022.html
