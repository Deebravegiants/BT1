# [M] GitProxy is vulnerable to a packfile parsing exploit

## Summary
Severity: Medium
Advisory: CVE-2025-54584
Aliases: GHSA-xxmh-rf63-qwjv
CVSS: 6.0 (CVSS:4.0/AV:N/AC:H/AT:N/PR:L/UI:N/VC:N/VI:H/VA:N/SC:N/SI:H/SA:N)
Published: 2025-07-30
Source: https://osv.dev/vulnerability/CVE-2025-54584
Type: osv

## Details
GitProxy is an application that stands between developers and a Git remote endpoint (e.g., github.com). In versions 1.19.1 and below, an attacker can craft a malicious Git packfile to exploit the PACK signature detection in the parsePush.ts file. By embedding a misleading PACK signature within commit content and carefully constructing the packet structure, the attacker can trick the parser into treating invalid or unintended data as the packfile. Potentially, this would allow bypassing approval or hiding commits. This issue is fixed in version 1.19.2.

## References
- https://github.com/finos/git-proxy/releases/tag/v1.19.2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/54xxx/CVE-2025-54584.json
- https://github.com/finos/git-proxy/security/advisories/GHSA-xxmh-rf63-qwjv
- https://nvd.nist.gov/vuln/detail/CVE-2025-54584
- https://github.com/finos/git-proxy/commit/333c98a165a5a1ec88414db3d4a2c6f81e083e0f
- https://github.com/finos/git-proxy/commit/a620a2f33c39c78e01783a274580bf822af3cc3a
