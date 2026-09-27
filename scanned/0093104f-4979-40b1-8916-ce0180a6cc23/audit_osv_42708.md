# [M] rsync 3.1.0 < 3.5.0 Signed Integer Overflow via MSG_IO_TIMEOUT

## Summary
Severity: Medium
Advisory: CVE-2026-70462
Aliases: GHSA-j9wh-5jmp-2m64
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-13
Source: https://osv.dev/vulnerability/CVE-2026-70462
Type: osv

## Details
rsync 3.1.0 before 3.5.0 contains a signed integer overflow vulnerability in the I/O timeout implementation that allows attackers to permanently disable connection timeouts by injecting MSG_IO_TIMEOUT messages carrying non-positive (zero or negative) values. Attackers can craft malicious MSG_IO_TIMEOUT messages that cause the timeout variable to wrap to a non-positive value, preventing the timeout check from firing and enabling idle or stalled connections to hold daemon slots indefinitely, leading to resource exhaustion.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/70xxx/CVE-2026-70462.json
- https://github.com/RsyncProject/rsync/releases/tag/v3.5.0
- https://github.com/RsyncProject/rsync/security/advisories/GHSA-j9wh-5jmp-2m64
- https://nvd.nist.gov/vuln/detail/CVE-2026-70462
- https://www.vulncheck.com/advisories/rsync-signed-integer-overflow-via-msg-io-timeout
- https://github.com/RsyncProject/rsync
