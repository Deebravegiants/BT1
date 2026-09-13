# [H] wifi: iwlwifi: mvm: guard against invalid STA ID on removal

## Summary
Severity: High
Advisory: CVE-2024-36921
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-30
Source: https://osv.dev/vulnerability/CVE-2024-36921
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.4.0 <6.6.31, >=6.7.0 <6.8.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: iwlwifi: mvm: guard against invalid STA ID on removal

Guard against invalid station IDs in iwl_mvm_mld_rm_sta_id as that would
result in out-of-bounds array accesses. This prevents issues should the
driver get into a bad state during error handling.

## References
- https://git.kernel.org/stable/c/17f64517bf5c26af56b6c3566273aad6646c3c4f
- https://git.kernel.org/stable/c/94f80a8ec15e238b78521f20f8afaed60521a294
- https://git.kernel.org/stable/c/fab21d220017daa5fd8a3d788ff25ccfecfaae2f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/36xxx/CVE-2024-36921.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-36921
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
