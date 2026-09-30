# [M] CVE-2026-40385

## Summary
Severity: Medium
Advisory: CVE-2026-40385
CVSS: 4.0 (CVSS:3.1/AV:L/AC:H/PR:N/UI:N/S:U/C:L/I:N/A:L)
Published: 2026-04-12
Source: https://osv.dev/vulnerability/CVE-2026-40385
Type: osv

## Details
In libexif through 0.6.25, an unsigned 32bit integer overflow in Nikon MakerNote handling could be used by local attackers to cause crashes or information leaks. This only affects 32bit systems.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/40xxx/CVE-2026-40385.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-40385
- https://github.com/libexif/libexif/commit/93003b93e50b3d259bd2227d8775b73a53c35d58
