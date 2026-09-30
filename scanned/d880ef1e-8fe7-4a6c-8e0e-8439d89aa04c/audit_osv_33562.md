# [H] Improper Pointer Arithmetic in pcl

## Summary
Severity: High
Advisory: CVE-2025-4638
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:H/VA:H/SC:N/SI:L/SA:H/AU:Y/R:U/V:D/RE:M/U:Amber)
Published: 2025-05-14
Source: https://osv.dev/vulnerability/CVE-2025-4638
Type: osv

## Details
A vulnerability exists in the inftrees.c component of the zlib library, which is bundled within the PointCloudLibrary (PCL). This issue may allow context-dependent attackers to cause undefined behavior by exploiting improper pointer arithmetic.

Since version 1.14.0, PCL by default uses a zlib installation from the system, unless the user sets WITH_SYSTEM_ZLIB=FALSE. So this potential vulnerability is only relevant if the PCL version is older than 1.14.0 or the user specifically requests to not use the system zlib.

## References
- https://github.com/PointCloudLibrary/pcl/blob/master/surface/CMakeLists.txt#L70
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/4xxx/CVE-2025-4638.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-4638
- https://github.com/PointCloudLibrary/pcl/commit/502bd2b013ce635f21632d523aa8cf2e04f7b7ac
- https://github.com/PointCloudLibrary/pcl/pull/6245
