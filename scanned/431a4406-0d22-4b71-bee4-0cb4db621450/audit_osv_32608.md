# [H] PeerTube ActivityPub Crawl Infinite Loop DoS

## Summary
Severity: High
Advisory: CVE-2025-32947
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-04-15
Source: https://osv.dev/vulnerability/CVE-2025-32947
Type: osv

## Details
This vulnerability allows any attacker to cause the PeerTube server to stop responding to requests due to an infinite loop in the "inbox" endpoint when receiving crafted ActivityPub activities.

## References
- https://github.com
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/32xxx/CVE-2025-32947.json
- https://github.com/Chocobozzz/PeerTube/releases/tag/v7.1.1
- https://nvd.nist.gov/vuln/detail/CVE-2025-32947
- https://research.jfrog.com/vulnerabilities/peertube-activitypub-crawl-dos/
- https://github.com/Chocobozzz/PeerTube/commit/76226d85685220db1495025300eca784d0336f7d
