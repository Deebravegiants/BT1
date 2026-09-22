# [M] OpenPrinting CUPS: Authorization bypass via case-insensitive group-member lookup

## Summary
Severity: Medium
Advisory: CVE-2026-27447
Aliases: GHSA-v987-m8hp-phj9
CVSS: 4.8 (CVSS:3.1/AV:N/AC:H/PR:H/UI:R/S:U/C:H/I:L/A:N)
Published: 2026-04-03
Source: https://osv.dev/vulnerability/CVE-2026-27447
Type: osv

## Details
OpenPrinting CUPS is an open source printing system for Linux and other Unix-like operating systems. In versions 2.4.16 and prior, CUPS daemon (cupsd) contains an authorization bypass vulnerability due to case-insensitive username comparison during authorization checks. The vulnerability allows an unprivileged user to gain unauthorized access to restricted operations by using a user with a username that differs only in case from an authorized user. At time of publication, there are no publicly available patches.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/27xxx/CVE-2026-27447.json
- https://github.com/OpenPrinting/cups/security/advisories/GHSA-v987-m8hp-phj9
- https://nvd.nist.gov/vuln/detail/CVE-2026-27447
- https://github.com/OpenPrinting/cups/commit/88516bf6d9e34cef7a64a704b856b837f70cd220
