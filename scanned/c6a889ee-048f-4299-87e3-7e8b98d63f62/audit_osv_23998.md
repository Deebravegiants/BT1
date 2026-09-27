# [M] phy: qcom-qmp-combo: fix NULL-deref on runtime resume

## Summary
Severity: Medium
Advisory: CVE-2022-49848
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-05-01
Source: https://osv.dev/vulnerability/CVE-2022-49848
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.0.0 <6.0.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

phy: qcom-qmp-combo: fix NULL-deref on runtime resume

Commit fc64623637da ("phy: qcom-qmp-combo,usb: add support for separate
PCS_USB region") started treating the PCS_USB registers as potentially
separate from the PCS registers but used the wrong base when no PCS_USB
offset has been provided.

Fix the PCS_USB base used at runtime resume to prevent dereferencing a
NULL pointer on platforms that do not provide a PCS_USB offset (e.g.
SC7180).

## References
- https://git.kernel.org/stable/c/04948e757148f870a31f4887ea2239403f516c3c
- https://git.kernel.org/stable/c/c559a8b5cfa3db196ced0257b288f17027621348
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49848.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49848
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
