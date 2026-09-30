# [M] liboqs: Heap-buffer-overflow in XMSS verification path via OID-controlled parameter mismatch (xmss_commons.c:194)

## Summary
Severity: Medium
Advisory: CVE-2026-46344
Aliases: GHSA-2wxh-55qf-c7wg
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2026-05-29
Source: https://osv.dev/vulnerability/CVE-2026-46344
Type: osv

## Details
liboqs is a C-language cryptographic library that provides implementations of post-quantum cryptography algorithms. Prior to 0.16.0, an out-of-bounds read has been identified in the XMSS and XMSS^MT stateful signature verification code. When the verification function is called with a correctly-sized signature buffer for the declared algorithm but a public key whose OID bytes (pk[0..3]) reference a different XMSS parameter set with a larger sig_bytes, the implementation re-parses the OID from the public key inside xmss_sign_open / xmssmt_sign_open and uses the resulting (larger) sig_bytes to index the caller-supplied signature buffer. As with CVE-2026-44518, the out-of-bounds bytes are consumed only as input to an internal hash computation and are not returned to the caller, so no oracle exists to leak their contents to an attacker. The primary observable effect is a possible crash (denial of service) of the verifying process if the read crosses into an unmapped memory page. This vulnerability is fixed in 0.16.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/46xxx/CVE-2026-46344.json
- https://github.com/open-quantum-safe/liboqs/security/advisories/GHSA-2wxh-55qf-c7wg
- https://nvd.nist.gov/vuln/detail/CVE-2026-46344
- https://github.com/open-quantum-safe/liboqs/commit/077e32a94f39af02209dbbc680bf8a43b774b305
