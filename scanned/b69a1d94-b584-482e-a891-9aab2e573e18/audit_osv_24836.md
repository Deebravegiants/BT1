# [H] Insufficient authorization validation between zones when xCAT zones are enabled

## Summary
Severity: High
Advisory: CVE-2023-27486
Aliases: GHSA-hpxg-7428-6jvv
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2023-03-08
Source: https://osv.dev/vulnerability/CVE-2023-27486
Type: osv

## Details
xCAT is a toolkit for deployment and administration of computer clusters. In versions prior to 2.16.5 if zones are configured as a mechanism to secure clusters in XCAT, it is possible for a local root user from one node to obtain credentials to SSH to any node in any zone, except the management node of the default zone. XCAT zones are not enabled by default. Only users that use the optional zone feature are impacted. All versions of xCAT prior to xCAT 2.16.5 are vulnerable. This problem has been fixed in xCAT 2.16.5. Users making use of zones should upgrade to 2.16.5. Users unable to upgrade may mitigate the issue by disabling zones or patching the management node with the fix contained in commit `85149c37f49`.

## References
- https://github.com/xcat2/xcat-core/pull/7247/commits/85149c37f49dbca7bd85f1f586960315604fc024
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/27xxx/CVE-2023-27486.json
- https://github.com/xcat2/xcat-core/security/advisories/GHSA-hpxg-7428-6jvv
- https://nvd.nist.gov/vuln/detail/CVE-2023-27486
- https://github.com/xcat2/xcat-core/issues/7246
- https://github.com/xcat2/xcat-core/pull/7247
