# [M] Tornado: Out-of-bounds memory access in C extension

## Summary
Severity: Medium
Advisory: CVE-2026-49854
Aliases: GHSA-cx3h-4qpv-8hc9, PYSEC-2026-3388
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2026-07-14
Source: https://osv.dev/vulnerability/CVE-2026-49854
Type: osv

## Details
Tornado is a Python web framework and asynchronous networking library. Prior to 6.5.6, the optional native extension tornado.speedups implemented websocket_mask without validating that the mask argument is exactly four bytes, allowing the C function to read up to three bytes beyond the provided buffer when reached through Tornado XSRF token decoding with the native extension active. This issue is fixed in version 6.5.6.

## References
- https://github.com/tornadoweb/tornado/releases/tag/v6.5.6
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/49xxx/CVE-2026-49854.json
- https://github.com/tornadoweb/tornado/security/advisories/GHSA-cx3h-4qpv-8hc9
- https://nvd.nist.gov/vuln/detail/CVE-2026-49854
- https://github.com/tornadoweb/tornado/commit/96dc88c2a05705287856b2cd6b4b4034f9a6aaac
- https://github.com/tornadoweb/tornado/pull/3626
