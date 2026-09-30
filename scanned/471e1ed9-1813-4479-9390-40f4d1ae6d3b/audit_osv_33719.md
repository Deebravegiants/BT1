# [M] Libtpms contains a possible out-of-bound access and abort due to HMAC signing issue

## Summary
Severity: Medium
Advisory: CVE-2025-49133
Aliases: GHSA-25w5-6fjj-hf8g
CVSS: 5.9 (CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:C/C:N/I:N/A:H)
Published: 2025-06-10
Source: https://osv.dev/vulnerability/CVE-2025-49133
Type: osv

## Details
Libtpms is a library that targets the integration of TPM functionality into hypervisors, primarily into Qemu. Libtpms, which is derived from the TPM 2.0 reference implementation code published by the Trusted Computing Group, is prone to a potential out of bounds (OOB) read vulnerability. The vulnerability occurs in the ‘CryptHmacSign’ function with an inconsistent pairing of the signKey and signScheme parameters, where the signKey is ALG_KEYEDHASH key and inScheme is an ECC or RSA scheme. The reported vulnerability is in the ‘CryptHmacSign’ function, which is defined in the "Part 4: Supporting Routines – Code" document, section "7.151 - /tpm/src/crypt/CryptUtil.c ". This vulnerability can be triggered from user-mode applications by sending malicious commands to a TPM 2.0/vTPM (swtpm) whose firmware is based on an affected TCG reference implementation. The effect on libtpms is that it will cause an abort due to the detection of the out-of-bounds access, thus for example making a vTPM (swtpm) unavailable to a VM. This vulnerability is fixed in 0.7.12, 0.8.10, 0.9.7, and 0.10.1.

## References
- https://trustedcomputinggroup.org/resource/tpm-library-specification
- https://trustedcomputinggroup.org/wp-content/uploads/TPM-2.0-1.83-Part-4-Supporting-Routines-Code.pdf
- https://www.kb.cert.org/vuls/id/282450
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/49xxx/CVE-2025-49133.json
- https://github.com/stefanberger/libtpms/security/advisories/GHSA-25w5-6fjj-hf8g
- https://nvd.nist.gov/vuln/detail/CVE-2025-49133
- https://github.com/stefanberger/libtpms/commit/04b2d8e9afc0a9b6bffe562a23e58c0de11532d1
