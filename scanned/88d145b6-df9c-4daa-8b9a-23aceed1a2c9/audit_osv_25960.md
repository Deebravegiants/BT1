# [C] Ability to DoS the testing infrastructure by overwriting files

## Summary
Severity: Critical
Advisory: CVE-2023-48310
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:H)
Published: 2023-11-20
Source: https://osv.dev/vulnerability/CVE-2023-48310
Type: osv

## Details
TestingPlatform is a testing platform for Internet Security Standards. Prior to version 2.1.1, user input is not filtered correctly. Nmap options are accepted. In this particular case, the option to create log files is accepted in addition to a host name (and even without). A log file is created at the location specified. These files are created as root. If the file exists, the existing file is being rendered useless. This can result in denial of service. Additionally, input for scanning can be any CIDR blocks passed to nmap. An attacker can scan 0.0.0.0/0 or even local networks. Version 2.1.1 contains a patch for this issue.

## References
- https://github.com/NC3-LU/TestingPlatform/releases/tag/v2.1.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/48xxx/CVE-2023-48310.json
- https://github.com/NC3-LU/TestingPlatform/security/advisories/GHSA-9fhc-f3mr-w6h6
- https://github.com/NC3-LU/TestingPlatform/security/advisories/GHSA-mmpf-rw6c-67mm
- https://nvd.nist.gov/vuln/detail/CVE-2023-48310
- https://github.com/NC3-LU/TestingPlatform/commit/7b3e7ca869a4845aa7445f874c22c5929315c3a7
