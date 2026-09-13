# [C] memory: tegra124-emc: Fix dll_change check

## Summary
Severity: Critical
Advisory: CVE-2026-53045
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-24
Source: https://osv.dev/vulnerability/CVE-2026-53045
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.2.0 <5.10.258, >=5.11.0 <5.15.209, >=5.16.0 <6.1.175, >=6.2.0 <6.6.141, >=6.7.0 <6.12.91, >=6.13.0 <6.18.33, >=6.19.0 <7.0.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

memory: tegra124-emc: Fix dll_change check

The code checking whether the specified memory timing enables DLL
in the EMRS register was reversed. DLL is enabled if bit A0 is low.
Fix the check.

## References
- https://git.kernel.org/stable/c/05f138fc7e27ee8e7a83ccf966c3fa26cda44dda
- https://git.kernel.org/stable/c/1793249c067a4b28e1aba0ad0e4d73aa9f9e165a
- https://git.kernel.org/stable/c/1ebbbef47d11cc90219c081492ccf995aaa3e9b3
- https://git.kernel.org/stable/c/2369b1831161356e1bcb51385d3e532dc4fe2771
- https://git.kernel.org/stable/c/7e19e72f306484996c52ff96cc92f69b78ed5435
- https://git.kernel.org/stable/c/9597ab9a8296ab337e6820f8a717ff621078b632
- https://git.kernel.org/stable/c/a85967331144fde9300be38bb44d2558eb6b742e
- https://git.kernel.org/stable/c/db0ae80865b515cc0b705c85877ec00f7eebe9fe
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53045.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53045
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
