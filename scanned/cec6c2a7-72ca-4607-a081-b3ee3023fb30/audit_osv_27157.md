# [C] eNMS TGZ File controller.py multiselect_filtering path traversal

## Summary
Severity: Critical
Advisory: CVE-2024-11664
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2024-11-25
Source: https://osv.dev/vulnerability/CVE-2024-11664
Type: osv

## Details
A vulnerability, which was classified as critical, has been found in eNMS up to 4.2. Affected by this issue is the function multiselect_filtering of the file eNMS/controller.py of the component TGZ File Handler. The manipulation leads to path traversal. The attack may be launched remotely. The exploit has been disclosed to the public and may be used. The patch is identified as 22b0b443acca740fc83b5544165c1f53eff3f529. It is recommended to apply a patch to fix this issue.

## References
- https://www.youtube.com/watch?v=FJVFtNb4_qA
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/11xxx/CVE-2024-11664.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-11664
- https://vuldb.com/?id.285986
- https://vuldb.com/?submit.447374
- https://github.com/eNMS-automation/eNMS/pull/419
- https://github.com/eNMS-automation/eNMS/pull/419#issuecomment-2495640750
- https://vuldb.com/?ctiid.285986
- https://github.com/eNMS-automation/eNMS/pull/419/commits/22b0b443acca740fc83b5544165c1f53eff3f529
- https://mega.nz/folder/ZhIiDQaI#TUJCRV-XN41L-WEVAu0sWg
