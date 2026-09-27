# [M] Cloud Hypervisor: Host File Exfiltration via QCOW Backing File Abuse

## Summary
Severity: Medium
Advisory: CVE-2026-27211
Aliases: GHSA-jmr4-g2hv-mjj6
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:N/VA:N/SC:H/SI:H/SA:H)
Published: 2026-02-21
Source: https://osv.dev/vulnerability/CVE-2026-27211
Type: osv

## Details
Cloud Hypervisor is a Virtual Machine Monitor for Cloud workloads. Versions 34.0 through 50.0 arevulnerable to arbitrary host file exfiltration (constrained by process privileges) when using virtio-block devices backed by raw images. A malicious guest can overwrite its disk header with a crafted QCOW2 structure pointing to a sensitive host path. Upon the next VM boot or disk scan, the image format auto-detection parses this header and serves the host file's contents to the guest. Guest-initiated VM reboots are sufficient to trigger a disk scan and do not cause the Cloud Hypervisor process to exit. Therefore, a single VM can perform this attack without needing interaction from the management stack. Successful exploitation requires the backing image to be either writable by the guest or sourced from an untrusted origin. Deployments utilizing only trusted, read-only images are not affected. This issue has been fixed in version 50.1. To workaround, enable land lock sandboxing and restrict process privileges and access.

## References
- https://github.com/cloud-hypervisor/cloud-hypervisor/releases/tag/v50.1
- https://github.com/cloud-hypervisor/cloud-hypervisor/releases/tag/v51.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/27xxx/CVE-2026-27211.json
- https://github.com/cloud-hypervisor/cloud-hypervisor/security/advisories/GHSA-jmr4-g2hv-mjj6
- https://nvd.nist.gov/vuln/detail/CVE-2026-27211
- https://github.com/cloud-hypervisor/cloud-hypervisor/commit/081a6ebb5184228ff348601502258f3f72bd8b43
- https://github.com/cloud-hypervisor/cloud-hypervisor/commit/509832298b6865365b00bda88722e76e41ce7f41
- https://github.com/cloud-hypervisor/cloud-hypervisor/commit/a63315df54e06f6ec867f17b63076c266e2d8648
- https://github.com/cloud-hypervisor/cloud-hypervisor/commit/cb495959a8bea1b56e8fc82d15ba527a0e7fcf3c
