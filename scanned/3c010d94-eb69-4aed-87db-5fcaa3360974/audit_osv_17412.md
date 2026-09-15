# [M] CVE-2020-15117

## Summary
Severity: Medium
Advisory: CVE-2020-15117
Aliases: GHSA-chfm-333q-gfpp
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-07-15
Source: https://osv.dev/vulnerability/CVE-2020-15117
Type: osv

## Details
In Synergy before version 1.12.0, a Synergy server can be crashed by receiving a kMsgHelloBack packet with a client name length set to 0xffffffff (4294967295) if the servers memory is less than 4 GB. It was verified that this issue does not cause a crash through the exception handler if the available memory of the Server is more than 4GB.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/VFDEQED64YLWQK2TF73EMXZDYX7YT2DD/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/WAQYCMBWNVCIEM27NPIKK3DGJCNBYLAK/
- https://github.com/symless/synergy-core/security/advisories/GHSA-chfm-333q-gfpp
- https://github.com/symless/synergy-core/commit/0a97c2be0da2d0df25cb86dfd642429e7a8bea39
