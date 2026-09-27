# [M] CVE-2020-24455

## Summary
Severity: Medium
Advisory: CVE-2020-24455
CVSS: 6.7 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-02-26
Source: https://osv.dev/vulnerability/CVE-2020-24455
Type: osv

## Details
Missing initialization of a variable in the TPM2 source may allow a privileged user to potentially enable an escalation of privilege via local access. This affects tpm2-tss before 3.0.1 and before 2.4.3.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/7KPOENCMJU4DMT3BDNUBRK25B3DJ47UO/
- https://github.com/tpm2-software/tpm2-tss/releases/tag/2.4.3
- https://github.com/tpm2-software/tpm2-tss/releases/tag/3.0.1
- https://security.gentoo.org/glsa/202107-10
- https://bugzilla.redhat.com/show_bug.cgi?id=1902167
