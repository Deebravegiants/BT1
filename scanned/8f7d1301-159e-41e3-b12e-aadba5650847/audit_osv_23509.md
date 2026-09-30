# [H] wifi: cfg80211: fix buffer overflow in elem comparison

## Summary
Severity: High
Advisory: CVE-2022-49023
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:H)
Published: 2024-10-21
Source: https://osv.dev/vulnerability/CVE-2022-49023
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.1.0 <5.4.226, >=5.5.0 <5.10.158, >=5.11.0 <5.15.82, >=5.16.0 <6.0.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: cfg80211: fix buffer overflow in elem comparison

For vendor elements, the code here assumes that 5 octets
are present without checking. Since the element itself is
already checked to fit, we only need to check the length.

## References
- https://git.kernel.org/stable/c/391cb872553627bdcf236c03ee7d5adb275e37e1
- https://git.kernel.org/stable/c/88a6fe3707888bd1893e9741157a7035c4159ab6
- https://git.kernel.org/stable/c/9e6b79a3cd17620d467311b30d56f2648f6880aa
- https://git.kernel.org/stable/c/9f16b5c82a025cd4c864737409234ddc44fb166a
- https://git.kernel.org/stable/c/f5c2ec288a865dbe3706b09bed12302e9f6d696b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49023.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49023
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
