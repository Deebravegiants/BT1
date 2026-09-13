# [M] PeerTube User Import Authenticated Resource Exhaustion

## Summary
Severity: Medium
Advisory: CVE-2025-32949
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-04-15
Source: https://osv.dev/vulnerability/CVE-2025-32949
Type: osv

## Details
This vulnerability allows any authenticated user to cause the server to consume very large amounts of disk space when extracting a Zip Bomb. 

If user import is enabled (which is the default setting), any registered user can upload an archive for importing. The code uses the yauzl library for reading the archive. The yauzl library does not contain any mechanism to detect or prevent extraction of a  Zip Bomb https://en.wikipedia.org/wiki/Zip_bomb . Therefore, when using the User Import functionality with a Zip Bomb, PeerTube will try extracting the archive which will cause a disk space resource exhaustion.

## References
- https://github.com
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/32xxx/CVE-2025-32949.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-32949
- https://research.jfrog.com/vulnerabilities/peertube-archive-resource-exhaustion/
- https://github.com/Chocobozzz/PeerTube/releases/tag/v7.1.1
