# [M] PCI: Fix active state requirement in PME polling

## Summary
Severity: Medium
Advisory: CVE-2024-26918
Ecosystem: Linux
CVSS: 6.2 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-04-17
Source: https://osv.dev/vulnerability/CVE-2024-26918
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.6.0 <6.6.18, >=6.7.0 <6.7.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

PCI: Fix active state requirement in PME polling

The commit noted in fixes added a bogus requirement that runtime PM managed
devices need to be in the RPM_ACTIVE state for PME polling.  In fact, only
devices in low power states should be polled.

However there's still a requirement that the device config space must be
accessible, which has implications for both the current state of the polled
device and the parent bridge, when present.  It's not sufficient to assume
the bridge remains in D0 and cases have been observed where the bridge
passes the D0 test, but the PM state indicates RPM_SUSPENDING and config
space of the polled device becomes inaccessible during pci_pme_wakeup().

Therefore, since the bridge is already effectively required to be in the
RPM_ACTIVE state, formalize this in the code and elevate the PM usage count
to maintain the state while polling the subordinate device.

This resolves a regression reported in the bugzilla below where a
Thunderbolt/USB4 hierarchy fails to scan for an attached NVMe endpoint
downstream of a bridge in a D3hot power state.

## References
- https://git.kernel.org/stable/c/41044d5360685e78a869d40a168491a70cdb7e73
- https://git.kernel.org/stable/c/63b1a3d9dd3b3f6d67f524e76270e66767090583
- https://git.kernel.org/stable/c/a4f12e5cbac2865c151d1e97e36eb24205afb23b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/26xxx/CVE-2024-26918.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-26918
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
