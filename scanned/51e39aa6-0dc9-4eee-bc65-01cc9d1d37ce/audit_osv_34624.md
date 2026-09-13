# [H] eprosima Fast DDS affected by Out-of-Memory in readPropertySeq via Manipulated DATA Submessage when DDS Security is enabled

## Summary
Severity: High
Advisory: CVE-2025-62599
Aliases: GHSA-fc3f-wcj5-5cph
CVSS: 8.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:N/I:N/A:H)
Published: 2026-02-03
Source: https://osv.dev/vulnerability/CVE-2025-62599
Type: osv

## Details
eprosima Fast DDS is a C++ implementation of the DDS (Data Distribution Service) standard of the OMG (Object Management Group). Prior to 2.6.11, 2.14.6, 3.2.4, 3.3.1, and 3.4.1, when the security mode is enabled, modifying the DATA Submessage within an SPDP packet sent by a publisher causes an Out-Of-Memory (OOM) condition, resulting in remote termination of Fast-DDS.
If the fields of PID_IDENTITY_TOKEN or PID_PERMISSION_TOKEN in the DATA Submessage — specifically by tampering with the length field in readPropertySeq — are modified, an integer overflow occurs, leading to an OOM during the resize operation. This vulnerability is fixed in 2.6.11, 2.14.6, 3.2.4, 3.3.1, and 3.4.1.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/62xxx/CVE-2025-62599.json
- https://github.com/eProsima/Fast-DDS/security/advisories/GHSA-fc3f-wcj5-5cph
- https://nvd.nist.gov/vuln/detail/CVE-2025-62599
