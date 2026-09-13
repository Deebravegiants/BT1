# [M] CVE-2021-27231

## Summary
Severity: Medium
Advisory: CVE-2021-27231
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N)
Published: 2021-02-16
Source: https://osv.dev/vulnerability/CVE-2021-27231
Type: osv

## Details
Hestia Control Panel 1.3.5 and below, in a shared-hosting environment, sometimes allows remote authenticated users to create a subdomain for a different customer's domain name, leading to spoofing of services or email messages.

## References
- https://github.com/hestiacp/hestiacp/issues/1622
- https://github.com/sickcodes/security/blob/master/advisories/sick-2021-006.md
- https://www.hestiacp.com/
- https://sick.codes/sick-2021-006
