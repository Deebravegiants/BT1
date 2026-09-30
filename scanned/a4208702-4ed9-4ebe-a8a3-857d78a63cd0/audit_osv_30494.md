# [M] wifi: iwlwifi: mvm: don't leak a link on AP removal

## Summary
Severity: Medium
Advisory: CVE-2024-53074
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-11-19
Source: https://osv.dev/vulnerability/CVE-2024-53074
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.9.0 <6.11.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: iwlwifi: mvm: don't leak a link on AP removal

Release the link mapping resource in AP removal. This impacted devices
that do not support the MLD API (9260 and down).
On those devices, we couldn't start the AP again after the AP has been
already started and stopped.

## References
- https://git.kernel.org/stable/c/3ed092997a004d68a3a5b0eeb94e71b69839d0f7
- https://git.kernel.org/stable/c/70ddf9ce1894c48dbbf10b0de51a95e4fb3dd376
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/53xxx/CVE-2024-53074.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-53074
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
