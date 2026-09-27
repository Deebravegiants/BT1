# [H] rsync < 3.5.0 Daemon IP Spoofing via PROXY Protocol Header

## Summary
Severity: High
Advisory: CVE-2026-53791
Aliases: GHSA-h2q9-5fr8-w635
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-13
Source: https://osv.dev/vulnerability/CVE-2026-53791
Type: osv

## Details
rsync daemon before 3.5.0 contains an IP address spoofing vulnerability that allows unauthenticated remote attackers to bypass IP-based access controls by sending a crafted PROXY protocol header with a forged source address. Attackers who can connect directly to the rsync daemon can inject a spoofed source IP in the PROXY protocol header to circumvent hosts allow/deny rules, gaining unauthorized access that would otherwise be blocked based on their real source address.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53791.json
- https://github.com/RsyncProject/rsync/releases/tag/v3.5.0
- https://github.com/RsyncProject/rsync/security/advisories/GHSA-h2q9-5fr8-w635
- https://nvd.nist.gov/vuln/detail/CVE-2026-53791
- https://www.vulncheck.com/advisories/rsync-daemon-ip-spoofing-via-proxy-protocol-header
- https://github.com/RsyncProject/rsync
