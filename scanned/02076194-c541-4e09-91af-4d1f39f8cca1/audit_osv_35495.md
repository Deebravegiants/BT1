# [H] Libucl: libucl: denial of service via embedded null byte in ucl input

## Summary
Severity: High
Advisory: CVE-2026-0708
CVSS: 8.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:L/A:H)
Published: 2026-03-17
Source: https://osv.dev/vulnerability/CVE-2026-0708
Type: osv

## Details
A flaw was found in libucl. A remote attacker could exploit this by providing a specially crafted Universal Configuration Language (UCL) input that contains a key with an embedded null byte. This can cause a segmentation fault (SEGV fault) in the `ucl_object_emit` function when parsing and emitting the object, leading to a Denial of Service (DoS) for the affected system.

## References
- https://access.redhat.com/security/cve/CVE-2026-0708
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/0xxx/CVE-2026-0708.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-0708
- https://bugzilla.redhat.com/show_bug.cgi?id=2427770
- https://github.com/vstakhov/libucl/issues/323
- https://github.com/vstakhov/libucl
