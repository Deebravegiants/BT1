# [M] net: dsa: microchip: ksz_common: Fix refcount leak bug

## Summary
Severity: Medium
Advisory: CVE-2022-49591
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49591
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.9.0 <5.15.58, >=5.16.0 <5.18.15

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: dsa: microchip: ksz_common: Fix refcount leak bug

In ksz_switch_register(), we should call of_node_put() for the
reference returned by of_get_child_by_name() which has increased
the refcount.

## References
- https://git.kernel.org/stable/c/4165e02716518bbbe9c9104b39530d40928bc7ce
- https://git.kernel.org/stable/c/88ec2ff42da3ac93b2437dc52fe25cd4372148e6
- https://git.kernel.org/stable/c/a14bd7475452c51835dd5a0cee4c8fa48dd0b539
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49591.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49591
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
