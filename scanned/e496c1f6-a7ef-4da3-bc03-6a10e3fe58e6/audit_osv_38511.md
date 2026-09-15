# [M] CVE-2026-40386

## Summary
Severity: Medium
Advisory: CVE-2026-40386
CVSS: 4.0 (CVSS:3.1/AV:L/AC:H/PR:N/UI:N/S:U/C:L/I:N/A:L)
Published: 2026-04-12
Source: https://osv.dev/vulnerability/CVE-2026-40386
Type: osv

## Details
In libexif through 0.6.25, an integer underflow in size checking for Fuji and Olympus MakerNote decoding could be used by attackers to crash or leak information out of libexif-using programs.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/40xxx/CVE-2026-40386.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-40386
- https://github.com/libexif/libexif/commit/dc6eac6e9655d14d0779d99e82d0f5f442d2f34b
