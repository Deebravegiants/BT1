# [H] s390/vfio-ap: always filter entire AP matrix

## Summary
Severity: High
Advisory: CVE-2024-26620
Ecosystem: Linux
CVSS: 8.2 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:H)
Published: 2024-02-29
Source: https://osv.dev/vulnerability/CVE-2024-26620
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.0.0 <6.1.76, >=6.2.0 <6.6.15, >=6.7.0 <6.7.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

s390/vfio-ap: always filter entire AP matrix

The vfio_ap_mdev_filter_matrix function is called whenever a new adapter or
domain is assigned to the mdev. The purpose of the function is to update
the guest's AP configuration by filtering the matrix of adapters and
domains assigned to the mdev. When an adapter or domain is assigned, only
the APQNs associated with the APID of the new adapter or APQI of the new
domain are inspected. If an APQN does not reference a queue device bound to
the vfio_ap device driver, then it's APID will be filtered from the mdev's
matrix when updating the guest's AP configuration.

Inspecting only the APID of the new adapter or APQI of the new domain will
result in passing AP queues through to a guest that are not bound to the
vfio_ap device driver under certain circumstances. Consider the following:

guest's AP configuration (all also assigned to the mdev's matrix):
14.0004
14.0005
14.0006
16.0004
16.0005
16.0006

unassign domain 4
unbind queue 16.0005
assign domain 4

When domain 4 is re-assigned, since only domain 4 will be inspected, the
APQNs that will be examined will be:
14.0004
16.0004

Since both of those APQNs reference queue devices that are bound to the
vfio_ap device driver, nothing will get filtered from the mdev's matrix
when updating the guest's AP configuration. Consequently, queue 16.0005
will get passed through despite not being bound to the driver. This
violates the linux device model requirement that a guest shall only be
given access to devices bound to the device driver facilitating their
pass-through.

To resolve this problem, every adapter and domain assigned to the mdev will
be inspected when filtering the mdev's matrix.

## References
- https://git.kernel.org/stable/c/850fb7fa8c684a4c6bf0e4b6978f4ddcc5d43d11
- https://git.kernel.org/stable/c/c69d821197611678533fb3eb784fc823b921349a
- https://git.kernel.org/stable/c/cdd134d56138302976685e6c7bc4755450b3880e
- https://git.kernel.org/stable/c/d6b8d034b576f406af920a7bee81606c027b24c6
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/26xxx/CVE-2024-26620.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-26620
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
