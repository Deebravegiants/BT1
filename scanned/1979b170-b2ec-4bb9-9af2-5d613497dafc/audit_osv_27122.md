# [M] Integer Underflow in DDS_Security_Deserialize_ methods may lead to OOB read

## Summary
Severity: Medium
Advisory: CVE-2024-10838
Aliases: GHSA-6jj6-w25p-jc42
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:L/VA:H/SC:N/SI:N/SA:N)
Published: 2025-03-12
Source: https://osv.dev/vulnerability/CVE-2024-10838
Type: osv

## Details
An integer underflow during deserialization may allow any unauthenticated user to read out of bounds heap memory. This may result into secret data or pointers revealing the layout of the address space to be included into a deserialized data structure, which may potentially lead to thread crashes or cause denial of service conditions.

## References
- https://github.com/eclipse-cyclonedds/cyclonedds/releases/tag/0.10.5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/10xxx/CVE-2024-10838.json
- https://github.com/eclipse-cyclonedds/cyclonedds/security/advisories/GHSA-6jj6-w25p-jc42
- https://nvd.nist.gov/vuln/detail/CVE-2024-10838
- https://gitlab.eclipse.org/security/cve-assignement/-/issues/46
- https://github.com/eclipse-cyclonedds/cyclonedds
