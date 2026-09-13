# [H] Sunshine vulnerable to remote unauthenticated arbitrary file read

## Summary
Severity: High
Advisory: CVE-2024-31220
Aliases: GHSA-6rg7-7m3w-w5wc
CVSS: 7.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L)
Published: 2024-04-05
Source: https://osv.dev/vulnerability/CVE-2024-31220
Type: osv

## Details
Sunshine is a self-hosted game stream host for Moonlight. Starting in version 0.16.0 and prior to version 0.18.0, an attacker may be able to remotely read arbitrary files without authentication due to a path traversal vulnerability. Users who exposed the Sunshine configuration web user interface outside of localhost may be affected, depending on firewall configuration. To exploit vulnerability, attacker could make an http/s request to the `node_modules` endpoint if user exposed Sunshine config web server to internet or attacker is on the LAN. Version 0.18.0 contains a patch for this issue. As a workaround, one may block access to Sunshine via firewall.

## References
- https://github.com/LizardByte/Sunshine/releases/tag/v0.18.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/31xxx/CVE-2024-31220.json
- https://github.com/LizardByte/Sunshine/security/advisories/GHSA-6rg7-7m3w-w5wc
- https://nvd.nist.gov/vuln/detail/CVE-2024-31220
