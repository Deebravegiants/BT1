# [M] nftables binding to an already bound chain

## Summary
Severity: Medium
Advisory: GHSA-jr8j-2jhp-m67v
Ecosystem: Go
Published: 2022-09-16
Source: https://github.com/advisories/GHSA-jr8j-2jhp-m67v
Type: github-advisory

## Affected
- Go: `github.com/siderolabs/talos` — affected >=0 <1.2.0

## Details
### Impact
An issue was discovered in net/netfilter/nf_tables_api.c in the Linux kernel. A denial of service can occur upon binding to an already bound chain.

Affected by this vulnerability is the function nft_verdict_init of the file net/netfilter/nf_tables_api.c. The manipulation with an unknown input leads to a denial of service vulnerability. The program does not release or incorrectly releases a resource before it is made available for re-use.

### Patches
The fix has been backported to [5.15.64](https://www.linuxkernelcves.com/cves/CVE-2022-39190) version of the upstream Linux kernel (5.15 is the upstream Kernel long term version Talos ships with). Talos >= v1.2.0 is shipped with Linux Kernel 5.15.64 fixing the above issue.

### Workarounds
It's recommended to upgrade

### References
- https://www.sesin.at/2022/09/02/cve-2022-39190-linux-kernel-up-to-5-19-5-nf_tables_api-c-nft_verdict_init-denial-of-service/
- https://nvd.nist.gov/vuln/detail/CVE-2022-39190

### For more information
- Email us at [security@siderolabs.com](mailto:security@siderolabs.com)

## References
- https://github.com/siderolabs/talos/security/advisories/GHSA-jr8j-2jhp-m67v
- https://github.com/siderolabs/talos
