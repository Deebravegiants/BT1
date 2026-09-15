# [H] Prevent DoS on deadlocked established channel in golang.org/x/crypto/ssh

## Summary
Severity: High
Advisory: CVE-2026-56855
Aliases: GO-2026-6355
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-09-02
Source: https://osv.dev/vulnerability/CVE-2026-56855
Type: osv

## Details
Previously, after a channel has been established, a malicious peer could send crafted messages that would deadlock the entire connection. Now, we handle all RFC 4254 channel messages; global requests are handled explicitly. Then, treat all other messages as a protocol error and tear the connection down instead of buffering and blocking.

## References
- https://go.dev/cl/826524
- https://go.dev/issue/81317
- https://groups.google.com/g/golang-announce/c/1y3fb2np35U
- https://pkg.go.dev
- https://pkg.go.dev/vuln/GO-2026-6355
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/56xxx/CVE-2026-56855.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-56855
