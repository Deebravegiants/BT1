# [M] CVE-2021-3623

## Summary
Severity: Medium
Advisory: CVE-2021-3623
CVSS: 6.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:H)
Published: 2022-03-02
Source: https://osv.dev/vulnerability/CVE-2021-3623
Type: osv

## Details
A flaw was found in libtpms. The flaw can be triggered by specially-crafted TPM 2 command packets containing illegal values and may lead to an out-of-bounds access when the volatile state of the TPM 2 is marshalled/written or unmarshalled/read. The highest threat from this vulnerability is to system availability.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/Z7KZSYMTE7Z4BBEZUWO2DIMQDWMGEP46/
- https://github.com/stefanberger/libtpms/pull/223
- https://bugzilla.redhat.com/show_bug.cgi?id=1976806
- https://github.com/stefanberger/libtpms/commit/2e6173c
- https://github.com/stefanberger/libtpms/commit/2f30d62
- https://github.com/stefanberger/libtpms/commit/7981d9a
