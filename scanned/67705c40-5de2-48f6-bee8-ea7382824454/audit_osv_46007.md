# [H] In GnuPG before 2.5.17, a stack-based buffer overflow exists in tpm2daemon during handling of the...

## Summary
Severity: High
Advisory: JLSEC-2026-565
Ecosystem: Julia
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-27
Source: https://osv.dev/vulnerability/JLSEC-2026-565
Type: osv

## Affected
- Julia: `GnuPG_jll` — affected >=2.5.16+0 <2.5.17+0

## Details
In GnuPG before 2.5.17, a stack-based buffer overflow exists in tpm2daemon during handling of the PKDECRYPT command for TPM-backed RSA and ECC keys.

## References
- https://access.redhat.com/errata/RHSA-2026:2719
- https://access.redhat.com/errata/RHSA-2026:2753
- https://access.redhat.com/security/cve/CVE-2026-24882
- https://bugzilla.redhat.com/show_bug.cgi?id=2433464
- https://dev.gnupg.org/T8045
- https://github.com/advisories/GHSA-mpc3-hqr8-w5f3
- https://nvd.nist.gov/vuln/detail/CVE-2026-24882
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-24882.json
- https://www.openwall.com/lists/oss-security/2026/01/27/8
