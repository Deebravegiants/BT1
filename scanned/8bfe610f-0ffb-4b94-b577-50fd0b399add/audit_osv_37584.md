# [M] Qemu-kvm: virtio-snd: integer overflow leading to unbounded memory allocation

## Summary
Severity: Medium
Advisory: CVE-2026-3196
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-06-19
Source: https://osv.dev/vulnerability/CVE-2026-3196
Type: osv

## Details
An integer overflow vulnerability was found in the virtio-snd device via PCM_INFO requests from the guest. A malicious guest can provide out-of-bounds stream counts, potentially leading to unbounded memory allocation on the host and a denial of service condition.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://access.redhat.com/security/cve/CVE-2026-3196
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/3xxx/CVE-2026-3196.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-3196
- https://bugzilla.redhat.com/show_bug.cgi?id=2443789
- https://gitlab.com/qemu-project/qemu
