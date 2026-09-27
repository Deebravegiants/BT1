# [M] PILOS Exposes PHP version

## Summary
Severity: Medium
Advisory: CVE-2025-62524
Aliases: GHSA-q93h-5j6h-j22x
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2025-10-27
Source: https://osv.dev/vulnerability/CVE-2025-62524
Type: osv

## Details
PILOS (Platform for Interactive Live-Online Seminars) is a frontend for BigBlueButton. PILOS before 4.8.0 exposes the PHP version via the X-Powered-By header, enabling attackers to fingerprint the server and assess potential exploits. This information disclosure vulnerability originates from PHP’s base image. Additionally, the PHP version can also be inferred through the PILOS version displayed in the footer and by examining the source code available on GitHub. This information disclosure vulnerability has been patched in PILOS in v4.8.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/62xxx/CVE-2025-62524.json
- https://github.com/THM-Health/PILOS/security/advisories/GHSA-q93h-5j6h-j22x
- https://nvd.nist.gov/vuln/detail/CVE-2025-62524
- https://github.com/THM-Health/PILOS/commit/14655bc4f8128ffd2b3c25004b01d9a802808da8
