# [M] mailcow ipixel flood attack leads to Denial of Service in admin page

## Summary
Severity: Medium
Advisory: CVE-2024-23824
Aliases: GHSA-45rv-3c5p-w4h7
CVSS: 4.7 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:L/I:L/A:L)
Published: 2024-02-02
Source: https://osv.dev/vulnerability/CVE-2024-23824
Type: osv

## Details
mailcow is a dockerized email package, with multiple containers linked in one bridged network. The application is vulnerable to pixel flood attack, once the payload has been successfully uploaded in the logo the application goes slow and doesn't respond in the admin page. It is tested on the versions 2023-12a and prior and patched in version 2024-01.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/23xxx/CVE-2024-23824.json
- https://github.com/mailcow/mailcow-dockerized/security/advisories/GHSA-45rv-3c5p-w4h7
- https://nvd.nist.gov/vuln/detail/CVE-2024-23824
- https://github.com/mailcow/mailcow-dockerized/commit/7f6f7e0e9ff608618e5b144bcf18d279610aa3ed
- https://github.com/0xbunniee/MailCow-Pixel-Flood-Attack
