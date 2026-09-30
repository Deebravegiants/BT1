# [C] MZ Automation libIEC61850 Stack-Based Buffer Overflow

## Summary
Severity: Critical
Advisory: CVE-2022-2970
CVSS: 10.0 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2022-09-23
Source: https://osv.dev/vulnerability/CVE-2022-2970
Type: osv

## Details
MZ Automation's libIEC61850 (versions 1.4 and prior; version 1.5 prior to commit a3b04b7bc4872a5a39e5de3fdc5fbde52c09e10e) does not sanitize input before memcpy is used, which could allow an attacker to crash the device or remotely execute arbitrary code.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/2xxx/CVE-2022-2970.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-2970
- https://www.cisa.gov/uscert/ics/advisories/icsa-22-251-01
