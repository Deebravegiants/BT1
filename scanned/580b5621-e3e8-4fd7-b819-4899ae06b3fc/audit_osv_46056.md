# [M] Rsync version 3.4.2 and prior contain an authorization bypass vulnerability in the rsync daemon's...

## Summary
Severity: Medium
Advisory: JLSEC-2026-628
Ecosystem: Julia
CVSS: 4.8 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2026-06-25
Source: https://osv.dev/vulnerability/JLSEC-2026-628
Type: osv

## Affected
- Julia: `rsync_jll` — affected >=0 <3.4.4+0

## Details
Rsync version 3.4.2 and prior contain an authorization bypass vulnerability in the rsync daemon's hostname-based access control list enforcement when configured with chroot. Attackers can bypass hostname-based deny rules by controlling the PTR record for their source IP address, allowing connections from hostnames that administrators intended to deny when reverse DNS resolution fails and defaults to UNKNOWN.

## References
- https://github.com/RsyncProject/rsync/releases/tag/v3.4.3
- https://github.com/RsyncProject/rsync/security/advisories/GHSA-rjfm-3w2m-jf4f
- https://github.com/advisories/GHSA-4j4q-473w-9q2r
- https://nvd.nist.gov/vuln/detail/CVE-2026-43617
- https://www.vulncheck.com/advisories/rsync-authorization-bypass-via-hostname-resolution
