# [H] wifi: cfg80211: reject auth/assoc to AP with our address

## Summary
Severity: High
Advisory: CVE-2023-53540
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:H)
Published: 2025-10-04
Source: https://osv.dev/vulnerability/CVE-2023-53540
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.32 <6.1.55, >=6.2.0 <6.5.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: cfg80211: reject auth/assoc to AP with our address

If the AP uses our own address as its MLD address or BSSID, then
clearly something's wrong. Reject such connections so we don't
try and fail later.

## References
- https://git.kernel.org/stable/c/07added2c6cd63de047bc786b39436322abb67c0
- https://git.kernel.org/stable/c/5d4e04bf3a0f098bd9033de3a5291810fa14c7a6
- https://git.kernel.org/stable/c/676a423410131d111a264d29aecbe6aadd57fb22
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53540.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53540
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
