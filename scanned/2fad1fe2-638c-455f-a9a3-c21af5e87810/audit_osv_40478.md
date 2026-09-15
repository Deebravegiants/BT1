# [H] Rapid7 Velociraptor Improper Input Validation in Client Message Handler

## Summary
Severity: High
Advisory: CVE-2026-5329
CVSS: 8.5 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-04-09
Source: https://osv.dev/vulnerability/CVE-2026-5329
Type: osv

## Details
Rapid7 Velociraptor versions prior to 0.76.2 contain an improper input validation vulnerability in the client monitoring message handler on the Velociraptor server (primarily Linux) that allows an authenticated remote attacker  to write to arbitrary internal server queues via a crafted monitoring message with a malicious queue name. The server handler that receives client monitoring messages does not sufficiently validate the queue name supplied by the client, allowing a rogue client to write arbitrary messages to privileged internal queues. This may lead to remote code execution on the Velociraptor server. Rapid7 Hosted Velociraptor instances are not affected by this vulnerability.

## References
- https://docs.velociraptor.app/announcements/advisories/cve-2026-5329/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/5xxx/CVE-2026-5329.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-5329
- https://github.com/Velocidex/velociraptor
