# [C] Dokploy: Command injection in writeTraefikConfigRemote via shell interpolation of unescaped YAML in SSH remote execution

## Summary
Severity: Critical
Advisory: CVE-2026-72735
Aliases: GHSA-478p-cx3j-hghc
CVSS: 9.9 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-72735
Type: osv

## Details
Dokploy is a free, self-hostable Platform as a Service (PaaS). Prior to 0.29.13, writeTraefikConfigRemote in packages/server/src/utils/traefik/application.ts serializes user-controlled Traefik configuration with yaml.stringify and interpolates the resulting yamlStr into an echo command executed through execAsyncRemote. Single quotes in redirect regex and replacement fields, basic authentication usernames, domain host values, or middleware configuration can terminate the shell quoting and execute arbitrary commands on managed remote servers with the configured SSH user's privileges. This vulnerability is caused by an incomplete fix for CVE-2026-45630. This issue is fixed in version 0.29.13.

## References
- https://github.com/Dokploy/dokploy/releases/tag/v0.29.13
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72735.json
- https://github.com/Dokploy/dokploy/security/advisories/GHSA-478p-cx3j-hghc
- https://nvd.nist.gov/vuln/detail/CVE-2026-72735
- https://github.com/Dokploy/dokploy/commit/92310ddb143c8e67ca95eb7db661838a76579f2e
