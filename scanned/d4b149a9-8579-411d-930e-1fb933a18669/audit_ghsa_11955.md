# [M] pypdf: manipulated stream length values can exhaust RAM

## Summary
Severity: Medium
Advisory: GHSA-hqmh-ppp3-xvm7
CVE: CVE-2026-31826
CWE: CWE-770
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:P/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-11
Source: https://github.com/advisories/GHSA-hqmh-ppp3-xvm7
Type: github-advisory

## Affected
- PyPI: `pypdf` — affected >=0 <6.8.0

## Details
### Impact

An attacker who uses this vulnerability can craft a PDF which leads to large memory usage. This requires parsing a content stream with a rather large `/Length` value, regardless of the actual data length inside the stream.

### Patches
This has been fixed in [pypdf==6.8.0](https://github.com/py-pdf/pypdf/releases/tag/6.8.0).

### Workarounds
If you cannot upgrade yet, consider applying the changes from PR [#3675](https://github.com/py-pdf/pypdf/pull/3675).

As far as we are aware, this mostly affects reading from buffers of unknown size, as returned by `open("file.pdf", mode="rb")` for example. Passing a file path or a `BytesIO` buffer to *pypdf* instead does not seem to trigger the vulnerability.

## References
- https://github.com/py-pdf/pypdf/security/advisories/GHSA-hqmh-ppp3-xvm7
- https://nvd.nist.gov/vuln/detail/CVE-2026-31826
- https://github.com/py-pdf/pypdf/pull/3675
- https://github.com/py-pdf/pypdf/commit/3c550b3196adeba1506a26e57c09c09fac75e9aa
- https://github.com/py-pdf/pypdf
- https://github.com/py-pdf/pypdf/releases/tag/6.8.0
