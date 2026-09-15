# [M] PeerTube User Import Authenticated Persistent Denial of Service

## Summary
Severity: Medium
Advisory: CVE-2025-32944
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-04-15
Source: https://osv.dev/vulnerability/CVE-2025-32944
Type: osv

## Details
The vulnerability allows any authenticated user to cause the PeerTube server to stop functioning in a persistent manner.  If user import is enabled (which is the default setting), any registered user can upload an archive for importing. The code uses the yauzl library for reading the archive. If the yauzl library encounters a filename that is considered illegal, it raises an exception that is uncaught by PeerTube, leading to a crash which repeats infinitely on startup.

## References
- https://github.com
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/32xxx/CVE-2025-32944.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-32944
- https://research.jfrog.com/vulnerabilities/peertube-archive-persistent-dos/
- https://github.com/Chocobozzz/PeerTube/releases/tag/v7.1.1
