# [H] Fast DDS does not verify Permissions CA

## Summary
Severity: High
Advisory: CVE-2025-24807
Aliases: GHSA-w33g-jmm2-8983
CVSS: 7.5 (CVSS:4.0/AV:L/AC:L/AT:N/PR:L/UI:N/VC:N/VI:H/VA:H/SC:N/SI:N/SA:N/E:U)
Published: 2025-02-11
Source: https://osv.dev/vulnerability/CVE-2025-24807
Type: osv

## Details
eprosima Fast DDS is a C++ implementation of the DDS (Data Distribution Service) standard of the OMG (Object Management Group). Prior to versions 2.6.10, 2.10.7, 2.14.5, 3.0.2, 3.1.2, and 3.2.0, per design, PermissionsCA is not full chain validated, nor is the expiration date validated. Access control plugin validates only the S/MIME signature which causes an expired PermissionsCA to be taken as valid. Even though this issue is responsible for allowing `governance/permissions` from an expired PermissionsCA and having the system crash when PermissionsCA is not self-signed and contains the full-chain, the impact is low. Versions 2.6.10, 2.10.7, 2.14.5, 3.0.2, 3.1.2, and 3.2.0 contain a fix for the issue.

## References
- https://github.com/eProsima/Fast-DDS/blob/2.6.9/src/cpp/security/accesscontrol/Permissions.cpp#L390-L396
- https://github.com/eProsima/Fast-DDS/blob/2.6.9/src/cpp/security/accesscontrol/Permissions.cpp#L412
- https://github.com/eProsima/Fast-DDS/blob/2.6.9/src/cpp/security/authentication/PKIDH.cpp#L241
- https://www.omg.org/spec/DDS-SECURITY/1.1/PDF
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/24xxx/CVE-2025-24807.json
- https://github.com/eProsima/Fast-DDS/security/advisories/GHSA-w33g-jmm2-8983
- https://nvd.nist.gov/vuln/detail/CVE-2025-24807
- https://github.com/eProsima/Fast-DDS/pull/5530
