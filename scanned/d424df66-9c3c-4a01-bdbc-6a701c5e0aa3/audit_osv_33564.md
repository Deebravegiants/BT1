# [M] Out-of-bounds Write in pcl

## Summary
Severity: Medium
Advisory: CVE-2025-4640
CVSS: 6.0 (CVSS:4.0/AV:N/AC:H/AT:N/PR:N/UI:N/VC:L/VI:L/VA:H/SC:N/SI:N/SA:N/AU:Y/R:U/V:C/RE:L/U:Amber)
Published: 2025-05-14
Source: https://osv.dev/vulnerability/CVE-2025-4640
Type: osv

## Details
Out-of-bounds Write vulnerability in PointCloudLibrary pcl allows Overflow Buffers. Since version 1.14.0, PCL by default uses a zlib installation from the system, unless the user sets WITH_SYSTEM_ZLIB=FALSE. So this potential vulnerability is only relevant if the PCL version is older than 1.14.0 or the user specifically requests to not use the system zlib.

## References
- https://github.com/PointCloudLibrary/pcl/blob/master/surface/CMakeLists.txt#L70
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/4xxx/CVE-2025-4640.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-4640
- https://github.com/PointCloudLibrary/pcl/commit/502bd2b013ce635f21632d523aa8cf2e04f7b7ac
- https://github.com/PointCloudLibrary/pcl/pull/6246
