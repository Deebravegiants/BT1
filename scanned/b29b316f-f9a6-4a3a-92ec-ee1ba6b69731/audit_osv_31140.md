# [M] wifi: iwlwifi: mvm: avoid NULL pointer dereference

## Summary
Severity: Medium
Advisory: CVE-2024-58062
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-03-06
Source: https://osv.dev/vulnerability/CVE-2024-58062
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.12.0 <6.12.13, >=6.13.0 <6.13.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: iwlwifi: mvm: avoid NULL pointer dereference

When iterating over the links of a vif, we need to make sure that the
pointer is valid (in other words - that the link exists) before
dereferncing it.
Use for_each_vif_active_link that also does the check.

## References
- https://git.kernel.org/stable/c/7f6fb4b7611eb6371c493c42fefad84a1742bcbb
- https://git.kernel.org/stable/c/cf704a7624f99eb2ffca1a16c69183e85544a613
- https://git.kernel.org/stable/c/fbb563ad5032a07ac83c746ce5c8de5f25b5ffd0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/58xxx/CVE-2024-58062.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-58062
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
