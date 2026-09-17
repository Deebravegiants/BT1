# [M] MeterSphere horizontal privilege escalation vulnerability of resources in project scope.

## Summary
Severity: Medium
Advisory: CVE-2023-50267
Aliases: GHSA-rcp4-c5p2-58v9
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N)
Published: 2023-12-28
Source: https://osv.dev/vulnerability/CVE-2023-50267
Type: osv

## Details
MeterSphere is a one-stop open source continuous testing platform. Prior to 2.10.10-lts, the authenticated attackers can update resources which don't belong to him if the resource ID is known. This issue if fixed in 2.10.10-lts.  There are no known workarounds.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/50xxx/CVE-2023-50267.json
- https://github.com/metersphere/metersphere/security/advisories/GHSA-rcp4-c5p2-58v9
- https://nvd.nist.gov/vuln/detail/CVE-2023-50267
