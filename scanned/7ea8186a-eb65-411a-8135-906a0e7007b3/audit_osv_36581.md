# [C] HUSTOJ has Arbitrary File Write (Zip Slip) in Problem Import Modules that leads to RCE

## Summary
Severity: Critical
Advisory: CVE-2026-24479
Aliases: GHSA-xmgg-2rw4-7fxj
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-01-27
Source: https://osv.dev/vulnerability/CVE-2026-24479
Type: osv

## Details
HUSTOF is an open source online judge based on PHP/C++/MySQL/Linux for ACM/ICPC and NOIP training. Prior to version 26.01.24, the problem_import_qduoj.php and problem_import_hoj.php modules fail to properly sanitize filenames within uploaded ZIP archives. Attackers can craft a malicious ZIP file containing files with path traversal sequences (e.g., ../../shell.php). When extracted by the server, this allows writing files to arbitrary locations in the web root, leading to Remote Code Execution (RCE). Version 26.01.24 contains a fix for the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/24xxx/CVE-2026-24479.json
- https://github.com/zhblue/hustoj/security/advisories/GHSA-xmgg-2rw4-7fxj
- https://nvd.nist.gov/vuln/detail/CVE-2026-24479
- https://github.com/zhblue/hustoj/commit/902bd09e6d0011fe89cd84d4236899314b33101f
