# [M] Incomplete control character validation in http.cookies

## Summary
Severity: Medium
Advisory: CVE-2026-3644
Aliases: PSF-2026-11
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:L/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-03-16
Source: https://osv.dev/vulnerability/CVE-2026-3644
Type: osv

## Details
The fix for CVE-2026-0672, which rejected control characters in http.cookies.Morsel, was incomplete. The Morsel.update(), |= operator, and unpickling paths were not patched, allowing control characters to bypass input validation. Additionally, BaseCookie.js_output() lacked the output validation applied to BaseCookie.output().

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/3xxx/CVE-2026-3644.json
- https://mail.python.org/archives/list/security-announce@python.org/thread/H6CADMBCDRFGWCMOXWUIHFJNV43GABJ7/
- https://nvd.nist.gov/vuln/detail/CVE-2026-3644
- https://github.com/python/cpython/issues/145599
- https://github.com/python/cpython/commit/3974092b037f9a3b000fb15b48ea61ce3b25d330
- https://github.com/python/cpython/commit/556aa098e738b127c714866f819b4abe2f7593d8
- https://github.com/python/cpython/commit/57e88c1cf95e1481b94ae57abe1010469d47a6b4
- https://github.com/python/cpython/commit/62ceb396fcbe69da1ded3702de586f4072b590dd
- https://github.com/python/cpython/commit/d16ecc6c3626f0e2cc8f08c309c83934e8a979dd
- https://github.com/python/cpython/commit/dae4b1a21f8df4570e30986affd61bbe4ade4cef
- https://github.com/python/cpython/pull/145600
- https://github.com/python/cpython
