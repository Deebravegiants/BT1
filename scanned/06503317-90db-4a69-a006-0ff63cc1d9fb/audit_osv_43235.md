# [C] Dokploy: Command Injection via dockerImage in buildRemoteDocker

## Summary
Severity: Critical
Advisory: CVE-2026-72877
Aliases: GHSA-jxxj-gmpx-h5rj
CVSS: 9.6 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:N)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-72877
Type: osv

## Details
Dokploy is a free, self-hostable Platform as a Service (PaaS). Prior to 0.29.13, the dockerImage field is interpolated without quoting into shell commands in buildRemoteDocker() in packages/server/src/utils/providers/docker.ts and is validated only as an optional string. An authenticated user with application create or update permission can use shell command substitution in dockerImage to execute arbitrary commands on the local build host or a remote SSH build target, exposing host secrets and other projects. This issue is fixed in version 0.29.13.

## References
- https://github.com/Dokploy/dokploy/releases/tag/v0.29.13
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72877.json
- https://github.com/Dokploy/dokploy/security/advisories/GHSA-jxxj-gmpx-h5rj
- https://nvd.nist.gov/vuln/detail/CVE-2026-72877
- https://github.com/Dokploy/dokploy/commit/cba0b253c7de4157dd932de7f16a2ad247c7cee9
- https://github.com/Dokploy/dokploy/pull/4860
