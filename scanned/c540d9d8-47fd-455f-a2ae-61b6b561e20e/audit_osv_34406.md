# [M] BunnyPad Vulnerable to Buffer Overflow When Opening Files of Size 20MB or Greater

## Summary
Severity: Medium
Advisory: CVE-2025-59418
Aliases: GHSA-qhw4-c7x5-vxmj
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2025-09-22
Source: https://osv.dev/vulnerability/CVE-2025-59418
Type: osv

## Details
BunnyPad is a note taking software. Prior to version 11.0.27000.0915, opening files greater than or equal to 20MB causes buffer overflow to occur. This issue has been patched in version 11.0.27000.0915. Users who wish not to upgrade should refrain from opening files larger than 10MB.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/59xxx/CVE-2025-59418.json
- https://github.com/GSYT-Productions/BunnyPad-SRC/security/advisories/GHSA-qhw4-c7x5-vxmj
- https://nvd.nist.gov/vuln/detail/CVE-2025-59418
- https://github.com/GSYT-Productions/BunnyPad-SRC/commit/d9224eb5e13c24ac148a77dff93e53c21f066533
