# [M] OpenRazer Vulnerable to Out of Bounds Read

## Summary
Severity: Medium
Advisory: CVE-2025-32776
Aliases: GHSA-835j-6976-46jx
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2025-04-15
Source: https://osv.dev/vulnerability/CVE-2025-32776
Type: osv

## Details
OpenRazer is an open source driver and user-space daemon to control Razer device lighting and other features on GNU/Linux. By writing specially crafted data to the `matrix_custom_frame` file, an attacker can cause the custom kernel driver to read more bytes than provided by user space. This data will be written into the RGB arguments which will be sent to the USB device. This issue has been patched in v3.10.2.

## References
- https://lists.debian.org/debian-lts-announce/2025/04/msg00032.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/32xxx/CVE-2025-32776.json
- https://github.com/openrazer/openrazer/security/advisories/GHSA-835j-6976-46jx
- https://nvd.nist.gov/vuln/detail/CVE-2025-32776
- https://github.com/openrazer/openrazer/issues/2433
- https://github.com/openrazer/openrazer/commit/57610511d2548eda66999eaed5aa4517e89d6d39
- https://github.com/openrazer/openrazer/commit/d869abd20995b4931795e1cde54d4ac84d9ca62f
