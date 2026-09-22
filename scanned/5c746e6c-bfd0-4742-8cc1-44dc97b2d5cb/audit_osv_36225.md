# [H] CVE-2026-2219

## Summary
Severity: High
Advisory: CVE-2026-2219
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-03-07
Source: https://osv.dev/vulnerability/CVE-2026-2219
Type: osv

## Details
It was discovered that dpkg-deb (a component of dpkg, the Debian package management system) does not properly validate the end of the data stream when uncompressing a zstd-compressed .deb archive, which may result in denial of service (infinite loop spinning the CPU).

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/2xxx/CVE-2026-2219.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-2219
- https://bugs.debian.org/1129722
- https://git.dpkg.org/cgit/dpkg/dpkg.git/commit/?id=6610297a62c0780dd0e80b0e302ef64fdcc9d313
