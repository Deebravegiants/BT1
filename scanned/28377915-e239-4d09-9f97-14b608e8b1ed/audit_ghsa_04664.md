# [M] OpenStack Nova: Nova scheduler hint injection bypasses Placement resource claims and scheduling constraints

## Summary
Severity: Medium
Advisory: GHSA-mfg3-p6m3-gjgr
CVE: CVE-2026-46448
CWE: CWE-669
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:L (CVSS_V3)
Published: 2026-06-16
Source: https://github.com/advisories/GHSA-mfg3-p6m3-gjgr
Type: github-advisory

## Affected
- PyPI: `nova` — affected >=18.0.0
- PyPI: `nova` — affected >=32.0.0 <32.2.1
- PyPI: `nova` — affected >=33.0.0 <33.0.2

## Details
## Affects

- Nova: >=18.0.0 <31.3.1, >=32.0.0 <32.2.1, >=33.0.0 <33.0.2


## Description
Erichen from the Institute of Computing Technology, Chinese Academy of 
Sciences reported that Nova's server create API does not strip internal 
scheduler hints. An authenticated user can bypass Placement resource 
claims and scheduling constraint enforcement, including availability 
zone, host aggregate, and image trait restrictions. The resulting 
instance has no Placement allocation, which can lead to compute node 
resource exhaustion and cross-tenant data persistence on NVMe devices 
after instance deletion. Deployments running Nova 18.0.0 or later are 
affected.



## Patches

- https://review.opendev.org/993604 (2025.1/epoxy)
- https://review.opendev.org/993603 (2025.2/flamingo)
- https://review.opendev.org/993602 (2026.1/gazpacho)
- https://review.opendev.org/993601 (2026.2/hibiscus)


## Credits
- Erichen from Institute of Computing Technology, Chinese Academy of 
Sciences (CVE-2026-46448)

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-46448
- https://bugs.launchpad.net/nova/+bug/2151252
- https://github.com/advisories/GHSA-mfg3-p6m3-gjgr
- https://github.com/openstack/nova
- https://github.com/pypa/advisory-database/tree/main/vulns/nova/PYSEC-2026-2686.yaml
- https://pypi.org/project/nova
- https://review.opendev.org/993601
- https://review.opendev.org/993602
- https://review.opendev.org/993603
- https://review.opendev.org/993604
- https://www.openwall.com/lists/oss-security/2026/06/16/5
- http://www.openwall.com/lists/oss-security/2026/06/16/5
