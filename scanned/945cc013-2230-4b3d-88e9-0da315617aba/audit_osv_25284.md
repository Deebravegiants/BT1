# [M] Triggerable assertion due to race condition in hot-unplug

## Summary
Severity: Medium
Advisory: CVE-2023-3301
CVSS: 5.6 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:C/C:N/I:N/A:H)
Published: 2023-09-13
Source: https://osv.dev/vulnerability/CVE-2023-3301
Type: osv

## Details
A flaw was found in QEMU. The async nature of hot-unplug enables a race scenario where the net device backend is cleared before the virtio-net pci frontend has been unplugged. A malicious guest could use this time window to trigger an assertion and cause a denial of service.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://packages.fedoraproject.org/
- https://access.redhat.com/security/cve/CVE-2023-3301
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/3xxx/CVE-2023-3301.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-3301
- https://security.netapp.com/advisory/ntap-20231020-0008/
- https://bugzilla.redhat.com/show_bug.cgi?id=2215784
