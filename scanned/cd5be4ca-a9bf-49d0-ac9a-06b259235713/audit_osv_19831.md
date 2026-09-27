# [M] CVE-2021-26539

## Summary
Severity: Medium
Advisory: CVE-2021-26539
Aliases: GHSA-rjqq-98f6-6j3r
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2021-02-08
Source: https://osv.dev/vulnerability/CVE-2021-26539
Type: osv

## Details
Apostrophe Technologies sanitize-html before 2.3.1 does not properly handle internationalized domain name (IDN) which could allow an attacker to bypass hostname whitelist validation set by the "allowedIframeHostnames" option.

## References
- https://github.com/apostrophecms/sanitize-html/blob/main/CHANGELOG.md#231-2021-01-22
- https://github.com/apostrophecms/sanitize-html/pull/458
- https://advisory.checkmarx.net/advisory/CX-2021-4308
