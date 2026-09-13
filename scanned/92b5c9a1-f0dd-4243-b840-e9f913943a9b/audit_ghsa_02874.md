# [M] Credential Disclosure in System.DirectoryServices.Protocols

## Summary
Severity: Medium
Advisory: GHSA-9cxh-gqpx-qc5m
CVE: CVE-2021-41355
CWE: CWE-200
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:A/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2021-10-12
Source: https://github.com/advisories/GHSA-9cxh-gqpx-qc5m
Type: github-advisory

## Affected
- NuGet: `System.DirectoryServices.Protocols` — affected >=0 <5.0.1

## Details
Microsoft is releasing this security advisory to provide information about a vulnerability in .NET. This advisory also provides guidance on what developers can do to update their applications to remove this vulnerability.

A Information Disclosure vulnerability exists in .NET where System.DirectoryServices.Protocols.LdapConnection may send credentials in plain text on Linux.

### Patches
Any .NET application that uses `System.DirectoryServices.Protocols` with a vulnerable version listed below on system based on Linux.

Package name | Vulnerable versions | Secure versions
------------ | ---------------- | -------------------------
System.DirectoryServices.Protocols | 5.0.0  | 5.0.1

### Other Details

- Announcement for this issue can be found at dotnet/announcements#202
- An Issue for this can be found at https://github.com/dotnet/runtime/issues/60301
- MSRC details for this can be found at https://msrc.microsoft.com/update-guide/en-US/vulnerability/CVE-2021-41355

## References
- https://github.com/dotnet/runtime/security/advisories/GHSA-9cxh-gqpx-qc5m
- https://nvd.nist.gov/vuln/detail/CVE-2021-41355
- https://github.com/dotnet/runtime/issues/60301
- https://github.com/dotnet/runtime
- https://msrc.microsoft.com/update-guide/en-US/vulnerability/CVE-2021-41355
- https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2021-41355
- https://www.oracle.com/security-alerts/cpujan2022.html
