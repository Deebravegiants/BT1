# [M] Microsoft: CBC Padding Oracle in Azure Blob Storage Encryption Library

## Summary
Severity: Medium
Advisory: GHSA-64x4-9hc6-r2h6
CVE: CVE-2022-30187
CWE: CWE-668
Ecosystem: Maven, NuGet, PyPI
CVSS: CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-07-13
Source: https://github.com/advisories/GHSA-64x4-9hc6-r2h6
Type: github-advisory

## Affected
- NuGet: `Azure.Storage.Queues` — affected >=0 <12.11.0
- NuGet: `Azure.Storage.Blobs` — affected >=0 <12.13.0
- Maven: `com.azure:azure-storage-blob` — affected >=0 <12.18.0
- PyPI: `azure-storage-queue` — affected >=0 <12.4.0
- PyPI: `azure-storage-blob` — affected >=0 <12.13.0

## Details
### Summary

The Azure Storage Encryption library in Java and other languages is vulnerable to a CBC Padding Oracle attack, similar to CVE-2020-8911. The library is not vulnerable to the equivalent of CVE-2020-8912, but only because it currently only supports AES-CBC as encryption mode. 

### Severity

Moderate - The vulnerability poses insider risks/privilege escalation risks, circumventing controls for stored data.

### Further Analysis
The Java Azure Blob Storage Encryption SDK is impacted by an issue that can result in loss of confidentiality and message forgery. The attack requires write access to the container in question, and that the attacker has access to an endpoint that reveals decryption failures (without revealing the plaintext) and that when encrypting the CBC option was chosen as content cipher.

This advisory describes the plaintext revealing vulnerabilities in the Java Azure Blob Storage Encryption SDK, with a similar issue in the other blob storage SDKs being present as well.

In the current version of the Azure Blob Storage crypto SDK, the only algorithm option that allows users to encrypt files is to AES-CBC, without computing a MAC on the data.

This exposes a padding oracle vulnerability: If the attacker has write access to the blob container bucket and can observe whether or not an endpoint with access to the key can decrypt a file (without observing the file contents that the endpoint learns in the process), they can reconstruct the plaintext with (on average) 128*length(plaintext) queries to the endpoint, by exploiting CBC's ability to manipulate the bytes of the next block and PKCS5 padding errors.

### Timeline
**Date reported**: March 29 2022
**Date preview**: June 16 2022
**Date GA**: July 11 2022
**Date disclosed**: July 17 2022

## References
- https://github.com/google/security-research/security/advisories/GHSA-6m8q-r22q-vfxh
- https://nvd.nist.gov/vuln/detail/CVE-2022-30187
- https://msrc.microsoft.com/update-guide/vulnerability/CVE-2022-30187
- https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2022-30187
