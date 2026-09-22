# [H] CVE-2026-24882

## Summary
Severity: High
Advisory: CVE-2026-24882
CVSS: 8.4 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-01-27
Source: https://osv.dev/vulnerability/CVE-2026-24882
Type: osv

## Details
In GnuPG before 2.5.17, a stack-based buffer overflow exists in tpm2daemon during handling of the PKDECRYPT command for TPM-backed RSA and ECC keys.

## References
- https://dev.gnupg.org/T8045
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-24882.json
- https://www.openwall.com/lists/oss-security/2026/01/27/8
- https://access.redhat.com/errata/RHSA-2026:2719
- https://access.redhat.com/errata/RHSA-2026:2753
- https://access.redhat.com/security/cve/CVE-2026-24882
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/24xxx/CVE-2026-24882.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-24882
- https://bugzilla.redhat.com/show_bug.cgi?id=2433464
