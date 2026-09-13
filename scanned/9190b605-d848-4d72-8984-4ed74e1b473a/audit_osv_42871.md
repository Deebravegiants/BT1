# [H] cpu: hotplug: Bound hotplug states sysfs output

## Summary
Severity: High
Advisory: CVE-2026-72066
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72066
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.6.0 <5.10.265, >=5.11.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

cpu: hotplug: Bound hotplug states sysfs output

states_show() adds CPU hotplug state names into a single sysfs buffer
using sprintf(). With enough registered states, this can write past the
end of the PAGE_SIZE buffer.

Use sysfs_emit_at() so output is bounded.

## References
- https://git.kernel.org/stable/c/2408be459c70ef4250da1a9e50f5478e6b250d61
- https://git.kernel.org/stable/c/27481cf4365a6ff5c9be3590143e7ed434000266
- https://git.kernel.org/stable/c/61a73a123ac7a7fbc57382531f8cb7092d569aba
- https://git.kernel.org/stable/c/631d53102da9f469c96b882b770336bec095b833
- https://git.kernel.org/stable/c/6cb15b81ff545840048fb0e1a6e827d560dbf367
- https://git.kernel.org/stable/c/86f436567f2516a0083b210bedc933544826a2c3
- https://git.kernel.org/stable/c/998f66e9ce320f3433f60b948e3698b744754a46
- https://git.kernel.org/stable/c/de4d3d8ae17dc8b4cf8c59436c4b7e2dc2491635
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72066.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72066
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
