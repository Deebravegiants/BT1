# [C] Dokploy: OS Command Injection via Bitbucket `owner`/`repository` in `git clone`

## Summary
Severity: Critical
Advisory: CVE-2026-72872
Aliases: GHSA-grrj-6xrh-j6vp
CVSS: 9.9 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-72872
Type: osv

## Details
Dokploy is a free, self-hostable Platform as a Service (PaaS). Prior to 0.29.13, application.saveBitbucketProvider stores bitbucketOwner and bitbucketRepository without validation and cloneBitbucketRepository in packages/server/src/utils/providers/bitbucket.ts interpolates those values into git clone commands executed through execAsync or execAsyncRemote, allowing a member with service deployment permission to execute arbitrary operating system commands on the Dokploy host or target server. This issue is fixed in version 0.29.13.

## References
- https://github.com/Dokploy/dokploy/releases/tag/v0.29.13
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72872.json
- https://github.com/Dokploy/dokploy/security/advisories/GHSA-grrj-6xrh-j6vp
- https://nvd.nist.gov/vuln/detail/CVE-2026-72872
- https://github.com/Dokploy/dokploy/commit/47347ab885b0ad1f5d0ef0e5e74bbba35c7f93bc
- https://github.com/Dokploy/dokploy/pull/4855
