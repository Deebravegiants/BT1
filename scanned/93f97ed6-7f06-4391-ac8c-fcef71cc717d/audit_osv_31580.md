# [M] Qemu-kvm: unbounded allocation in virtio-crypto

## Summary
Severity: Medium
Advisory: CVE-2025-14876
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-02-18
Source: https://osv.dev/vulnerability/CVE-2025-14876
Type: osv

## Details
A flaw was found in the virtio-crypto device of QEMU. A malicious guest operating system can exploit a missing length limit in the AKCIPHER path, leading to uncontrolled memory allocation. This can result in a denial of service (DoS) on the host system by causing the QEMU process to terminate unexpectedly.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://access.redhat.com/security/cve/CVE-2025-14876
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/14xxx/CVE-2025-14876.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-14876
- https://bugzilla.redhat.com/show_bug.cgi?id=2423549
- https://gitlab.com/qemu-project/qemu
