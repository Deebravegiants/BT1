# [M] CVE-2021-26927

## Summary
Severity: Medium
Advisory: CVE-2021-26927
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2021-02-23
Source: https://osv.dev/vulnerability/CVE-2021-26927
Type: osv

## Details
A flaw was found in jasper before 2.0.25. A null pointer dereference in jp2_decode in jp2_dec.c may lead to program crash and denial of service.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/JSXESYUHMO522Z3RHXOQ2SJNWP3XTO67/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/JYVCFVTVPL66OS7LCNLUSYCMYQAVWXMM/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/YRZFZSJ4UVLLMXSKHR455TAC2SD3TOHI/
- https://github.com/jasper-software/jasper/commit/41f214b121b837fa30d9ca5f2430212110f5cd9b
- https://github.com/jasper-software/jasper/issues/265
