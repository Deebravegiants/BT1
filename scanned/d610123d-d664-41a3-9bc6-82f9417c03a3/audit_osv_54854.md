# [H] CVE-2024-53432

## Summary
Severity: High
Advisory: CVE-2024-53432
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-11-21
Source: https://osv.dev/vulnerability/CVE-2024-53432
Type: osv

## Details
While parsing certain malformed PLY files, PCL version 1.14.1 crashes due to an uncaught std::out_of_range exception in PCLPointCloud2::at. This issue could potentially be exploited to cause a denial-of-service (DoS) attack when processing untrusted PLY files.

## References
- https://github.com/PointCloudLibrary/pcl/issues/6162
