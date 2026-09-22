# [H] libsignal-service-rs Doesn't Check Origin of Sync Messages

## Summary
Severity: High
Advisory: CVE-2025-24903
Aliases: GHSA-r58q-66g9-h6g8
CVSS: 8.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:H/A:N)
Published: 2025-02-13
Source: https://osv.dev/vulnerability/CVE-2025-24903
Type: osv

## Details
libsignal-service-rs is a Rust version of the libsignal-service-java library which implements the core functionality to communicate with Signal servers. Prior to commit 82d70f6720e762898f34ae76b0894b0297d9b2f8, any contact may forge a sync message, impersonating another device of the local user. The origin of sync messages is not checked. Patched libsignal-service can be found after commit 82d70f6720e762898f34ae76b0894b0297d9b2f8. The `Metadata` struct contains an additional `was_encrypted` field, which breaks the API, but should be easily resolvable. No known workarounds are available.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/24xxx/CVE-2025-24903.json
- https://github.com/whisperfish/libsignal-service-rs/security/advisories/GHSA-r58q-66g9-h6g8
- https://nvd.nist.gov/vuln/detail/CVE-2025-24903
- https://github.com/whisperfish/libsignal-service-rs/commit/82d70f6720e762898f34ae76b0894b0297d9b2f8
