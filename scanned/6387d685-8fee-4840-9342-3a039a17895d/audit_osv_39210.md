# [M] liboqs: XMSS Buffer Overread Bug

## Summary
Severity: Medium
Advisory: CVE-2026-44518
Aliases: GHSA-wf7v-fhxj-73m2
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2026-05-29
Source: https://osv.dev/vulnerability/CVE-2026-44518
Type: osv

## Details
liboqs is a C-language cryptographic library that provides implementations of post-quantum cryptography algorithms. Prior to 0.16.0, an out-of-bounds read has been identified in the XMSS and XMSS^MT stateful signature verification code. When the verification function is called with a signature buffer shorter than the expected signature size for the given parameter set, the implementation does not validate the caller-supplied length and proceeds to read past the end of the buffer. The out-of-bounds bytes are consumed only as input to an internal hash computation and are not returned to the caller, so no oracle exists to leak their contents to an attacker. The primary observable effect is a possible crash (denial of service) of the verifying process if the read crosses into an unmapped memory page. This vulnerability is fixed in 0.16.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/44xxx/CVE-2026-44518.json
- https://github.com/open-quantum-safe/liboqs/security/advisories/GHSA-wf7v-fhxj-73m2
- https://nvd.nist.gov/vuln/detail/CVE-2026-44518
- https://github.com/open-quantum-safe/liboqs/commit/ef70dea7c85e5637f37828d75e5b9bb29dbfe513
