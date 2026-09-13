# [H] wifi: cfg80211: validate HE operation element parsing

## Summary
Severity: High
Advisory: CVE-2024-40930
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:H)
Published: 2024-07-12
Source: https://osv.dev/vulnerability/CVE-2024-40930
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.8.0 <6.9.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: cfg80211: validate HE operation element parsing

Validate that the HE operation element has the correct
length before parsing it.

## References
- https://git.kernel.org/stable/c/4dc3a3893dae5a7f73e5809273aca0f1f3548d55
- https://git.kernel.org/stable/c/f15e3e13e14cc5ae8f950c16efe706add18ac8e2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/40xxx/CVE-2024-40930.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-40930
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
