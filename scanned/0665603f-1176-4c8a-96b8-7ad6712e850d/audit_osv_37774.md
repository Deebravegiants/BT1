# [H] AutoGPT: Unauthenticated DoS via Disk Space Exhaustion

## Summary
Severity: High
Advisory: CVE-2026-33232
Aliases: GHSA-374w-2pxq-c9jp
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-05-19
Source: https://osv.dev/vulnerability/CVE-2026-33232
Type: osv

## Details
AutoGPT is a workflow automation platform for creating, deploying, and managing continuous artificial intelligence agents. Versions 0.4.2 through 0.6.51 are vulnerable to an unauthenticated Denial of Service (DoS) through the server due to uncontrolled disk space consumption. The download_agent_file endpoint creates persistent temporary files for every request but fails to delete them after they are served. An unauthenticated attacker can repeatedly call this endpoint to exhaust the server's disk space, causing
 the database or other system services to fail due to "No space left on device" errors, rendering the entire AutoGPT Platform backend unavailable to all users. This issue has been patched in version 0.6.52.

## References
- https://github.com/Significant-Gravitas/AutoGPT/releases/tag/autogpt-platform-beta-v0.6.52
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/33xxx/CVE-2026-33232.json
- https://github.com/Significant-Gravitas/AutoGPT/security/advisories/GHSA-374w-2pxq-c9jp
- https://nvd.nist.gov/vuln/detail/CVE-2026-33232
