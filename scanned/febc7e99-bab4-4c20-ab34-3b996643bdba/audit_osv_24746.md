# [H] CVE-2023-2597

## Summary
Severity: High
Advisory: CVE-2023-2597
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-05-22
Source: https://osv.dev/vulnerability/CVE-2023-2597
Type: osv

## Details
In Eclipse Openj9 before version 0.38.0, in the implementation of the shared cache (which is enabled by default in OpenJ9 builds) the size of a string is not properly checked against the size of the buffer.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/2xxx/CVE-2023-2597.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-2597
- https://security.netapp.com/advisory/ntap-20240621-0006/
- https://github.com/eclipse-openj9/openj9/pull/17259
