# [M] powercap: arm_scmi: Remove recursion while parsing zones

## Summary
Severity: Medium
Advisory: CVE-2023-53428
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-18
Source: https://osv.dev/vulnerability/CVE-2023-53428
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.2.0 <6.4.16, >=6.5.0 <6.5.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

powercap: arm_scmi: Remove recursion while parsing zones

Powercap zones can be defined as arranged in a hierarchy of trees and when
registering a zone with powercap_register_zone(), the kernel powercap
subsystem expects this to happen starting from the root zones down to the
leaves; on the other side, de-registration by powercap_deregister_zone()
must begin from the leaf zones.

Available SCMI powercap zones are retrieved dynamically from the platform
at probe time and, while any defined hierarchy between the zones is
described properly in the zones descriptor, the platform returns the
availables zones with no particular well-defined order: as a consequence,
the trees possibly composing the hierarchy of zones have to be somehow
walked properly to register the retrieved zones from the root.

Currently the ARM SCMI Powercap driver walks the zones using a recursive
algorithm; this approach, even though correct and tested can lead to kernel
stack overflow when processing a returned hierarchy of zones composed by
particularly high trees.

Avoid possible kernel stack overflow by substituting the recursive approach
with an iterative one supported by a dynamically allocated stack-like data
structure.

## References
- https://git.kernel.org/stable/c/3e767d6850f867cc33ac16ca097350a1d2417982
- https://git.kernel.org/stable/c/8022b64fb7daa6135d9f7b0e2f7b5b8e9e5179c9
- https://git.kernel.org/stable/c/b427c23cebc5c926516f20304bf1acc05a33d147
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53428.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53428
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
