# [M] CVE-2021-3505

## Summary
Severity: Medium
Advisory: CVE-2021-3505
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2021-04-19
Source: https://osv.dev/vulnerability/CVE-2021-3505
Type: osv

## Details
A flaw was found in libtpms in versions before 0.8.0. The TPM 2 implementation returns 2048 bit keys with ~1984 bit strength due to a bug in the TCG specification. The bug is in the key creation algorithm in RsaAdjustPrimeCandidate(), which is called before the prime number check. The highest threat from this vulnerability is to data confidentiality.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/NUCZX4S53TUNTSGTCRDNOQZV2V2RI4RJ/
- https://bugzilla.redhat.com/show_bug.cgi?id=1950046
- https://github.com/stefanberger/libtpms/issues/183
