# [H] um: virtio_uml: Fix use-after-free after put_device in probe

## Summary
Severity: High
Advisory: CVE-2025-39951
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-10-04
Source: https://osv.dev/vulnerability/CVE-2025-39951
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.5.0 <5.10.245, >=5.11.0 <5.15.194, >=5.16.0 <6.1.154, >=6.2.0 <6.6.108, >=6.7.0 <6.12.49, >=6.13.0 <6.16.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

um: virtio_uml: Fix use-after-free after put_device in probe

When register_virtio_device() fails in virtio_uml_probe(),
the code sets vu_dev->registered = 1 even though
the device was not successfully registered.
This can lead to use-after-free or other issues.

## References
- https://git.kernel.org/stable/c/00e98b5a69034b251bb36dc6e7123d7648e218e4
- https://git.kernel.org/stable/c/14c231959a16ca41bfdcaede72483362a8c645d7
- https://git.kernel.org/stable/c/4f364023ddcfe83f7073b973a9cb98584b7f2a46
- https://git.kernel.org/stable/c/5e94e44c9cb30d7a383d8ac227f24a8c9326b770
- https://git.kernel.org/stable/c/7ebf70cf181651fe3f2e44e95e7e5073d594c9c0
- https://git.kernel.org/stable/c/aaf900a83508c8cd5cdf765e7749f9076196ec7f
- https://git.kernel.org/stable/c/c2ff91255e0157b356cff115d8dc3eeb5162edf2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/39xxx/CVE-2025-39951.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-39951
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
