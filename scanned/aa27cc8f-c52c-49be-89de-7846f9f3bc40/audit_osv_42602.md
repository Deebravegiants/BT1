# [H] Wekan: SSRF filter bypass via DNS-resolving hostname in outgoing webhooks (incomplete fix of CVE-2026-53446)

## Summary
Severity: High
Advisory: CVE-2026-68558
Aliases: GHSA-66m2-4wfr-c45p
CVSS: 8.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:L/A:N)
Published: 2026-08-19
Source: https://osv.dev/vulnerability/CVE-2026-68558
Type: osv

## Details
Wekan is open source kanban built with Meteor. From 8.36 until 9.74, the outgoing webhook Integration URL validator in models/integrations.js checked only the literal URL.hostname against regular expressions, so DNS names such as 169-254-169-254.nip.io passed that first-line check. The delivery path's fetchSafe guard already blocked the reported IPv4 destination, but its separate IPv4-only resolver and duplicated blocklist created inconsistent all-address-family enforcement and drift risk between input-time and connection-time validation. Version 9.74 makes server/lib/ssrfGuard.js resolve all addresses with `dns.lookup({ all: true })`, validate every result through the shared isIpBlocked logic, pin the connection, and block redirects. This issue is fixed in version 9.74.

## References
- https://github.com/wekan/wekan/releases/tag/v9.74
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68558.json
- https://github.com/wekan/wekan/security/advisories/GHSA-66m2-4wfr-c45p
- https://nvd.nist.gov/vuln/detail/CVE-2026-68558
- https://github.com/wekan/wekan/commit/ef845fe4a0adb82af436313310939cd48c0b1347
