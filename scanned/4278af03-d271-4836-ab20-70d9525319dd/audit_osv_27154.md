# [M] CVE-2024-11584

## Summary
Severity: Medium
Advisory: CVE-2024-11584
CVSS: 5.9 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L)
Published: 2025-06-26
Source: https://osv.dev/vulnerability/CVE-2024-11584
Type: osv

## Details
cloud-init through 25.1.2 includes the systemd socket unit cloud-init-hotplugd.socket with default SocketMode that grants 0666 permissions, making it world-writable. This is used for the "/run/cloud-init/hook-hotplug-cmd" FIFO. An unprivileged user could trigger hotplug-hook commands.

## References
- https://github.com/canonical/cloud-init/pull/6265/commits/6e10240a7f0a2d6110b398640b3fd46cfa9a7cf3
- https://github.com/canonical/cloud-init/releases/tag/25.1.3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/11xxx/CVE-2024-11584.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-11584
- https://github.com/canonical/cloud-init
