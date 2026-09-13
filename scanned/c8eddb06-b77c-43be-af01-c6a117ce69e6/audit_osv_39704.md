# [M] `openvm-pairing` pairing check missing proper subfield check on scaling factor

## Summary
Severity: Medium
Advisory: CVE-2026-46669
Aliases: GHSA-76mq-v757-53gr
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-06-10
Source: https://osv.dev/vulnerability/CVE-2026-46669
Type: osv

## Details
OpenVM is a performant and modular zkVM framework built for customization and extensibility. Prior to version 1.6.0, the openvm-pairing guest library's try_honest_pairing_check function invokes Theorem 3 of https://eprint.iacr.org/2024/640.pdf but does not check that the scaling factor s is in a proper subfield of Fp12. This allows incorrect results to the pairing check. This issue has been patched in version 1.6.0.

## References
- https://github.com/openvm-org/openvm/releases/tag/v1.6.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/46xxx/CVE-2026-46669.json
- https://github.com/openvm-org/openvm/security/advisories/GHSA-76mq-v757-53gr
- https://nvd.nist.gov/vuln/detail/CVE-2026-46669
