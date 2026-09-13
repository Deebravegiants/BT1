# [M] crypto: caam - Fix the pointer passed to caam_qi_shutdown()

## Summary
Severity: Medium
Advisory: CVE-2024-56754
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-12-29
Source: https://osv.dev/vulnerability/CVE-2024-56754
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.5.0 <5.10.231, >=5.11.0 <5.15.174, >=5.16.0 <6.1.120, >=6.2.0 <6.6.64, >=6.7.0 <6.11.11, >=6.12.0 <6.12.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

crypto: caam - Fix the pointer passed to caam_qi_shutdown()

The type of the last parameter given to devm_add_action_or_reset() is
"struct caam_drv_private *", but in caam_qi_shutdown(), it is casted to
"struct device *".

Pass the correct parameter to devm_add_action_or_reset() so that the
resources are released as expected.

## References
- https://git.kernel.org/stable/c/1f8e2f597b918ca5827a5c6d00b819d064264d1c
- https://git.kernel.org/stable/c/6187727e57aec122c8a99c464c74578c810cbe40
- https://git.kernel.org/stable/c/66eddb8dcb61065c53098510165f14b54232bcc2
- https://git.kernel.org/stable/c/84a185aea7b83f620699de0ea36907d588d89cf6
- https://git.kernel.org/stable/c/ad39df0898d3f469776c19d99229be055cc2dcea
- https://git.kernel.org/stable/c/ad980b04f51f7fb503530bd1cb328ba5e75a250e
- https://git.kernel.org/stable/c/cc386170b3312fd7b5bc4a69a9f52d7f50814526
- https://lists.debian.org/debian-lts-announce/2025/03/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/56xxx/CVE-2024-56754.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-56754
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
