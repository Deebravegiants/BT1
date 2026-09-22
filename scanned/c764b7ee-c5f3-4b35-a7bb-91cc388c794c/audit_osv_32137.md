# [H] libsignal-service-rs doesn't sanity check plaintext envelopes are not sanity-checked

## Summary
Severity: High
Advisory: CVE-2025-24904
Aliases: GHSA-hrrc-wpfw-5hj2
CVSS: 8.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:H/A:N)
Published: 2025-02-13
Source: https://osv.dev/vulnerability/CVE-2025-24904
Type: osv

## Details
libsignal-service-rs is a Rust version of the libsignal-service-java library which implements the core functionality to communicate with Signal servers. Prior to commit 82d70f6720e762898f34ae76b0894b0297d9b2f8, plaintext content envelopes could be injected by a server or a malicious client, and may have been able to bypass the end-to-end encryption and authentication. The vulnerability is fixed per 82d70f6720e762898f34ae76b0894b0297d9b2f8. The `Metadata` struct contains an additional `was_encrypted` field, which breaks the API, but should be easily resolvable. No known workarounds are available.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/24xxx/CVE-2025-24904.json
- https://github.com/whisperfish/libsignal-service-rs/security/advisories/GHSA-hrrc-wpfw-5hj2
- https://nvd.nist.gov/vuln/detail/CVE-2025-24904
- https://github.com/whisperfish/libsignal-service-rs/commit/82d70f6720e762898f34ae76b0894b0297d9b2f8
