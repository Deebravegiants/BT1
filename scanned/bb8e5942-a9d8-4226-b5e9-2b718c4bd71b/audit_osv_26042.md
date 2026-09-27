# [H] CVE-2023-49958

## Summary
Severity: High
Advisory: CVE-2023-49958
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2023-12-07
Source: https://osv.dev/vulnerability/CVE-2023-49958
Type: osv

## Details
An issue was discovered in Dalmann OCPP.Core through 1.2.0 for OCPP (Open Charge Point Protocol) for electric vehicles. The server processes mishandle StartTransaction messages containing additional, arbitrary properties, or duplicate properties. The last occurrence of a duplicate property is accepted. This could be exploited to alter transaction records or impact system integrity.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/49xxx/CVE-2023-49958.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-49958
- https://github.com/dallmann-consulting/OCPP.Core/issues/36
