# [M] rsync 2.0.0 < 3.5.0 Connection Slot Exhaustion DoS via Handshake Stall

## Summary
Severity: Medium
Advisory: CVE-2026-70464
Aliases: GHSA-hrwq-ccf7-rw5m
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-13
Source: https://osv.dev/vulnerability/CVE-2026-70464
Type: osv

## Details
rsync daemon 2.0.0 before 3.5.0 contains a denial of service vulnerability that allows unauthenticated remote attackers to exhaust daemon connection slots by stalling the handshake process before or after module selection without triggering the I/O timeout. Attackers can open many simultaneous connections and trickle data at the minimum rate to avoid timeout, or stall entirely before module selection where no timeout applies, consuming all available connection slots and denying service to legitimate clients.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/70xxx/CVE-2026-70464.json
- https://github.com/RsyncProject/rsync/releases/tag/v3.5.0
- https://github.com/RsyncProject/rsync/security/advisories/GHSA-hrwq-ccf7-rw5m
- https://nvd.nist.gov/vuln/detail/CVE-2026-70464
- https://www.vulncheck.com/advisories/rsync-connection-slot-exhaustion-dos-via-handshake-stall
- https://github.com/RsyncProject/rsync
