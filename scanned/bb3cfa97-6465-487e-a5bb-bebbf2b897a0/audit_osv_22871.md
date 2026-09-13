# [M] NagVis CoreLogonMultisite.php checkAuthCookie type conversion

## Summary
Severity: Medium
Advisory: CVE-2022-3979
CVSS: 5.6 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:L)
Published: 2022-11-13
Source: https://osv.dev/vulnerability/CVE-2022-3979
Type: osv

## Details
A vulnerability was found in NagVis up to 1.9.33 and classified as problematic. This issue affects the function checkAuthCookie of the file share/server/core/classes/CoreLogonMultisite.php. The manipulation of the argument hash leads to incorrect type conversion. The attack may be initiated remotely. The complexity of an attack is rather high. The exploitation is known to be difficult. Upgrading to version 1.9.34 is able to address this issue. The identifier of the patch is 7574fd8a2903282c2e0d1feef5c4876763db21d5. It is recommended to upgrade the affected component. The identifier VDB-213557 was assigned to this vulnerability.

## References
- https://lists.debian.org/debian-lts-announce/2025/05/msg00000.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/3xxx/CVE-2022-3979.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-3979
- https://vuldb.com/?id.213557
- https://vuldb.com/?ctiid.213557
- https://github.com/NagVis/nagvis/commit/7574fd8a2903282c2e0d1feef5c4876763db21d5
- https://github.com/NagVis/nagvis/releases/tag/nagvis-1.9.34
- https://www.sonarsource.com/blog/checkmk-rce-chain-2/
