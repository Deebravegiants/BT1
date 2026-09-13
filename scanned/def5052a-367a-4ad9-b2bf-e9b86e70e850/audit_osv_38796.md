# [C] Postiz: Arbitrary Code Execution and Token Exfiltration in pr-docker-build.yml via untrusted Dockerfile.dev

## Summary
Severity: Critical
Advisory: CVE-2026-42298
Aliases: GHSA-v975-9h5p-xhm4
CVSS: 10.0 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-05-08
Source: https://osv.dev/vulnerability/CVE-2026-42298
Type: osv

## Details
Postiz is an AI social media scheduling tool. Prior to commit da44801, a "Pwn Request" vulnerability in the Build and Publish PR Docker Image workflow (.github/workflows/pr-docker-build.yml) allows any unauthenticated user to execute arbitrary code during the Docker build process and exfiltrate a highly privileged GITHUB_TOKEN (write-all permissions). This can be achieved simply by opening a Pull Request from a fork with a maliciously modified Dockerfile.dev. This issue has been patched via commit da44801.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/42xxx/CVE-2026-42298.json
- https://github.com/gitroomhq/postiz-app/security/advisories/GHSA-v975-9h5p-xhm4
- https://nvd.nist.gov/vuln/detail/CVE-2026-42298
- https://github.com/gitroomhq/postiz-app/commit/da448012dd87e94944cbe83a38e7fd023269ec46
