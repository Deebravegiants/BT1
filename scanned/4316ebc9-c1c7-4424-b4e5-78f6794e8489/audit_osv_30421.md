# [M] Nextcloud Server has incomplete sanitization of SVG files allows to embed other images into previews

## Summary
Severity: Medium
Advisory: CVE-2024-52515
Aliases: GHSA-5m5g-hw8c-2236
CVSS: 5.7 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:N/A:N)
Published: 2024-11-15
Source: https://osv.dev/vulnerability/CVE-2024-52515
Type: osv

## Details
Nextcloud Server is a self hosted personal cloud system. After an admin enables the default-disabled SVG preview provider, a malicious user could upload a manipulated SVG file referencing paths. If the file would exist the preview of the SVG would preview the other file instead. It is recommended that the Nextcloud Server is upgraded to 27.1.10, 28.0.6 or 29.0.1 and Nextcloud Enterprise Server is upgraded to 24.0.12.15, 25.0.13.10, 26.0.13.4, 27.1.10, 28.0.6 or 29.0.1.

## References
- https://hackerone.com/reports/2484499
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/52xxx/CVE-2024-52515.json
- https://github.com/nextcloud/security-advisories/security/advisories/GHSA-5m5g-hw8c-2236
- https://nvd.nist.gov/vuln/detail/CVE-2024-52515
- https://github.com/nextcloud/server/commit/7e1c30f82a63fbea8c269e0eec38291377f32604
- https://github.com/nextcloud/server/pull/45340
