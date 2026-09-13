# [M] keylime fails to flag device as untrusted when signature does not validate

## Summary
Severity: Medium
Advisory: GHSA-g4wg-cfpf-9689
CVE: CVE-2023-3674
CWE: CWE-1283
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2023-07-19
Source: https://github.com/advisories/GHSA-g4wg-cfpf-9689
Type: github-advisory

## Affected
- PyPI: `keylime` — affected >=0 <7.2.5

## Details
A flaw was found in the keylime attestation verifier, which fails to flag a device's submitted TPM quote as faulty when the quote's signature does not validate for some reason. Instead, it will only emit an error in the log without flagging the device as untrusted.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-3674
- https://github.com/keylime/keylime/commit/95ce3d86bd2c53009108ffda2dcf553312d733db
- https://access.redhat.com/errata/RHSA-2024:1139
- https://access.redhat.com/security/cve/CVE-2023-3674
- https://bugzilla.redhat.com/show_bug.cgi?id=2222903
- https://github.com/keylime/keylime
- https://github.com/pypa/advisory-database/tree/main/vulns/keylime/PYSEC-2023-128.yaml
