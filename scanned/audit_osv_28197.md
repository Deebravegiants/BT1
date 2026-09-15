# [C] Missing check in tpm2_checkquote allows attackers to misrepresent the TPM state

## Summary
Severity: Critical
Advisory: CVE-2024-29039
Aliases: GHSA-8rjm-5f5f-h4q6
CVSS: 9.0 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2024-06-28
Source: https://osv.dev/vulnerability/CVE-2024-29039
Type: osv

## Details
tpm2 is the source repository for the Trusted Platform Module (TPM2.0) tools. This vulnerability allows attackers to manipulate tpm2_checkquote outputs by altering the TPML_PCR_SELECTION in the PCR input file.  As a result, digest values are incorrectly mapped to PCR slots and banks, providing a misleading picture of the TPM state. This issue has been patched in version 5.7.

## References
- https://github.com/tpm2-software/tpm2-tools/releases/tag/5.7
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/EFR7SVEWCOXORHPCLLGXEMHFMIGG2MFE/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/GI4JFEZBKQQUPJ4RWK6IHEWXAFCEJDPI/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/29xxx/CVE-2024-29039.json
- https://github.com/tpm2-software/tpm2-tools/security/advisories/GHSA-8rjm-5f5f-h4q6
- https://nvd.nist.gov/vuln/detail/CVE-2024-29039
