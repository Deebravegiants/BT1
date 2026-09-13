# [H] rAthena map-server use-after-free vulnerability in RODEX

## Summary
Severity: High
Advisory: CVE-2025-62170
Aliases: GHSA-9mj9-8vgv-r92j
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-10-13
Source: https://osv.dev/vulnerability/CVE-2025-62170
Type: osv

## Details
rAthena is an open-source cross-platform MMORPG server. A use-after-free vulnerability exists in the RODEX functionality of rAthena's map-server in versions prior to commit af2f3ba. An unauthenticated attacker can exploit this vulnerability via a specific attacking scenario to cause a denial of service by crashing the map-server. This issue has been patched in commit af2f3ba. There are no known workarounds aside from manually applying the patch.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/62xxx/CVE-2025-62170.json
- https://github.com/rathena/rathena/security/advisories/GHSA-9mj9-8vgv-r92j
- https://nvd.nist.gov/vuln/detail/CVE-2025-62170
- https://github.com/rathena/rathena/commit/af2f3ba33fc03dc6dd510f8cfe84cd9185af748d
