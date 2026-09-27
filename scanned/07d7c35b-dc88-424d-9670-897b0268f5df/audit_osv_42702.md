# [M] rsync 3.4.2 < 3.5.0 DoS via --zt Zstandard Compression Thread Exhaustion

## Summary
Severity: Medium
Advisory: CVE-2026-70455
Aliases: GHSA-rjvj-qgqg-cvx9
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-13
Source: https://osv.dev/vulnerability/CVE-2026-70455
Type: osv

## Details
rsync 3.4.2 before 3.5.0 contains a denial of service vulnerability that allows a remote sender to exhaust system resources by specifying the --zt short alias for --compress-threads, which bypasses the refuse options directive's string matching on long option names. Attackers can specify --zt=N with a large value to spawn an unbounded number of Zstandard worker threads on the receiver, exhausting available thread and memory resources.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/70xxx/CVE-2026-70455.json
- https://github.com/RsyncProject/rsync/releases/tag/v3.5.0
- https://github.com/RsyncProject/rsync/security/advisories/GHSA-rjvj-qgqg-cvx9
- https://nvd.nist.gov/vuln/detail/CVE-2026-70455
- https://www.vulncheck.com/advisories/rsync-dos-via-zt-zstandard-compression-thread-exhaustion
- https://github.com/RsyncProject/rsync
