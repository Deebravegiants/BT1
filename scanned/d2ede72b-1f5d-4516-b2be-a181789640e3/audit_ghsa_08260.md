# [C] Security feature bypass vulnerability in Azure Key Vault Keys library for Java

## Summary
Severity: Critical
Advisory: GHSA-97jf-46m3-8953
CVE: CVE-2026-33117
CWE: CWE-287, CWE-347
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-05-12
Source: https://github.com/advisories/GHSA-97jf-46m3-8953
Type: github-advisory

## Affected
- Maven: `com.azure:azure-security-keyvault-keys` — affected >=0 <4.10.6

## Details
The Java Key Vault Keys library in the Azure SDK for Java contains an issue in the local cryptographic verification path where authentication tag comparison was implemented incorrectly. In affected applications that use the vulnerable local cryptography path, specially crafted encrypted input may bypass integrity verification checks. Operations delegated to the Key Vault service are not affected. The issue is addressed in version 4.10.6.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-33117
- https://github.com/Azure/azure-sdk-for-java/pull/48476
- https://github.com/Azure/azure-sdk-for-java/commit/1b5c5c79d85a5c9a9cfd07f6cdff6fd0f50eccf9
- https://github.com/Azure/azure-sdk-for-java
- https://msrc.microsoft.com/update-guide/vulnerability/CVE-2026-33117
