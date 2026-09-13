# [C] Galaxy vulnerable to unauthorized modification of pages/visualizations due to insufficient permission check

## Summary
Severity: Critical
Advisory: CVE-2023-27578
Aliases: GHSA-j8q2-r4g5-f22j
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:H)
Published: 2023-03-20
Source: https://osv.dev/vulnerability/CVE-2023-27578
Type: osv

## Details
Galaxy is an open-source platform for data analysis. All supported versions of Galaxy are affected prior to 22.01, 22.05, and 23.0 are affected by an insufficient permission check. Unsupported versions are likely affected as far back as the functionality of Visualizations/Pages exists. Due to this issue, an attacker can modify or delete any Galaxy Visualization or Galaxy Page given they know the encoded ID of it. Additionally, they can copy or import any Galaxy Visualization given they know the encoded ID of it. Patches are available for versions 22.01, 22.05, and 23.0. For the changes to take effect, you must restart all Galaxy server processes. There are no supported workarounds.

## References
- https://depot.galaxyproject.org/patch/GX-2022-0002/modify_pages_viz-release_22.01.patch
- https://depot.galaxyproject.org/patch/GX-2022-0002/modify_pages_viz-release_22.05.patch
- https://depot.galaxyproject.org/patch/GX-2022-0002/modify_pages_viz-release_23.0.patch
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/27xxx/CVE-2023-27578.json
- https://github.com/galaxyproject/galaxy/security/advisories/GHSA-j8q2-r4g5-f22j
- https://nvd.nist.gov/vuln/detail/CVE-2023-27578
