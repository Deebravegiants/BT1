# [M] Buffer Overlow in TSS2_RC_Decode in tpm2-tss

## Summary
Severity: Medium
Advisory: CVE-2023-22745
Aliases: GHSA-4j3v-fh23-vx67
CVSS: 6.4 (CVSS:3.1/AV:L/AC:H/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-01-19
Source: https://osv.dev/vulnerability/CVE-2023-22745
Type: osv

## Details
tpm2-tss is an open source software implementation of the Trusted Computing Group (TCG) Trusted Platform Module (TPM) 2 Software Stack (TSS2). In versions prior to 4.1.0-rc0, 4.0.1, and 3.2.2-rc1, `Tss2_RC_SetHandler` and `Tss2_RC_Decode` both index into `layer_handler` with an 8 bit layer number, but the array only has `TPM2_ERROR_TSS2_RC_LAYER_COUNT` entries, so trying to add a handler for higher-numbered layers or decode a response code with such a layer number reads/writes past the end of the buffer. This Buffer overrun, could result in arbitrary code execution. An example attack would be a MiTM bus attack that returns 0xFFFFFFFF for the RC. Given the common use case of TPM modules an attacker must have local access to the target machine with local system privileges which allows access to the TPM system. Usually TPM access requires administrative privilege. Versions 4.1.0-rc0, 4.0.1, and 3.2.2-rc1 fix the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/22xxx/CVE-2023-22745.json
- https://github.com/tpm2-software/tpm2-tss/security/advisories/GHSA-4j3v-fh23-vx67
- https://nvd.nist.gov/vuln/detail/CVE-2023-22745
- https://github.com/tpm2-software/tpm2-tss/commit/306490c8d848c367faa2d9df81f5e69dab46ffb5
- https://github.com/tpm2-software/tpm2-tss/commit/49107d65d5c7be430671398416bbd89dae4e34e7
- https://github.com/tpm2-software/tpm2-tss/commit/7ab42953216adec046d000a5e3085f3ee5e9cabf
