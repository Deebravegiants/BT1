# [M] The logic of get apk path in KernelSU module can be bypassed

## Summary
Severity: Medium
Advisory: CVE-2023-49794
Aliases: GHSA-8rc5-x54x-5qc4
CVSS: 6.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:R/S:U/C:H/I:H/A:H)
Published: 2024-01-02
Source: https://osv.dev/vulnerability/CVE-2023-49794
Type: osv

## Details
KernelSU is a Kernel-based root solution for Android devices. In versions 0.7.1 and prior, the logic of get apk path in KernelSU kernel module can be bypassed, which causes any malicious apk named `me.weishu.kernelsu` get root permission. If a KernelSU module installed device try to install any not checked apk which package name equal to the official KernelSU Manager, it can take over root privileges on the device. As of time of publication, a patched version is not available.

## References
- https://drive.google.com/file/d/1b9UrmG_co9EJXB_yMBneRArUIR5sTuaN/view?usp=drive_link
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/49xxx/CVE-2023-49794.json
- https://github.com/tiann/KernelSU/security/advisories/GHSA-8rc5-x54x-5qc4
- https://nvd.nist.gov/vuln/detail/CVE-2023-49794
