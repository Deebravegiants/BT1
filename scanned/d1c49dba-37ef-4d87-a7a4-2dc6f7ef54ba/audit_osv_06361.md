# [M] FTP PASV SSRF, ftpcp() does not use actual peer address, trusts server-supplied PASV host address

## Summary
Severity: Medium
Advisory: BIT-libpython-2026-8328
Aliases: BIT-python-2026-8328, BIT-python-min-2026-8328, CVE-2026-8328, PSF-0000-CVE-2026-8328, PSF-2026-24
Ecosystem: Bitnami
Published: 2026-06-05
Source: https://osv.dev/vulnerability/BIT-libpython-2026-8328
Type: osv

## Affected
- Bitnami: `libpython` — affected >=3.14.0 <3.14.6

## Details
The ftpcp() function in Lib/ftplib.py was not updated when 
CVE-2021-4189 was fixed. While makepasv() was patched to replace 
server-supplied PASV host addresses with the actual peer address 
(getpeername()[0]), ftpcp() still calls parse227() directly and passes 
the raw attacker-controllable IP address and port to target.sendport(). This patch is related to CVE-2021-4189.

## References
- https://github.com/python/cpython/issues/87451
- https://github.com/python/cpython/pull/149648
- https://mail.python.org/archives/list/security-announce@python.org/thread/ITF2BAPBQEPYK3LDMPRSY435JGNHYNDP/
- https://nvd.nist.gov/vuln/detail/CVE-2026-8328
- https://github.com/python/cpython/commit/5dadc64673ce875ebfb24163907777dae0f6ca06
- https://github.com/python/cpython/commit/7d95a1dc7382b55cba7fdd6a110336077584a4f0
- https://github.com/python/cpython/commit/bb3446dda6c49b32e67c11dbbbf221b40be00763
- https://github.com/python/cpython/commit/c88704431ea3248ca769384c13856330976fac1d
- https://github.com/python/cpython/commit/eac4fe3b2c77693790a5ef7dfab127c1fee81bf9
- https://github.com/python/cpython/commit/2bbcf3fb7a420a05605576c0f9468d4675381b5f
- https://github.com/python/cpython/commit/ef12d0dc824baccf737bba1458e5eed3d1e0fceb
