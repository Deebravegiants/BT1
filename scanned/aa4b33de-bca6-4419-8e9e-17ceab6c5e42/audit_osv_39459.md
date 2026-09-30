# [C] Open XDMoD Vulnerable to Unauthenticated SQL Injection Leading to Full Database Compromise

## Summary
Severity: Critical
Advisory: CVE-2026-45779
Aliases: GHSA-r33r-6g3c-r992
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-06-05
Source: https://osv.dev/vulnerability/CVE-2026-45779
Type: osv

## Details
OpenXDMoD is an open framework for collecting and analyzing HPC metrics. An SQL injection vulnerability exists in Open XDMoD versions prior to 10.0.3 that allows an unauthenticated remote attacker to execute arbitrary SQL statements. Exploitation requires no authentication or user interaction and can result in complete compromise of the underlying database. All deployments of Open XDMoD prior to 10.0.3 are impacted. This issue was discovered on 2023-08-03 and patched on 2023-08-04. At this time there is no evidence that this vulnerability has been exploited in the wild. The vulnerability was patched in Open XDMoD 10.0.3 on 2023-08-04. As a workaround, apply the patch manually.

## References
- https://github.com/ubccr/xdmod/releases/tag/v10.0.3
- https://open.xdmod.org/security_patches/GHSA-r33r-6g3c-r992-0_0_0-8_6_0.patch
- https://open.xdmod.org/security_patches/GHSA-r33r-6g3c-r992-9_0_0-10_0_2.patch
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45779.json
- https://github.com/ubccr/xdmod/security/advisories/GHSA-r33r-6g3c-r992
- https://nvd.nist.gov/vuln/detail/CVE-2026-45779
