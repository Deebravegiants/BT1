# [M] Qemu-kvm: heap buffer out-of-bounds read in vmdk compressed grain parsing

## Summary
Severity: Medium
Advisory: CVE-2026-2243
CVSS: 5.1 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:L)
Published: 2026-02-19
Source: https://osv.dev/vulnerability/CVE-2026-2243
Type: osv

## Details
A flaw was found in QEMU. A specially crafted VMDK image could trigger an out-of-bounds read vulnerability, potentially leading to a 12-byte leak of sensitive information or a denial of service condition (DoS).

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://access.redhat.com/security/cve/CVE-2026-2243
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/2xxx/CVE-2026-2243.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-2243
- https://bugzilla.redhat.com/show_bug.cgi?id=2440934
- https://gitlab.com/qemu-project/qemu
