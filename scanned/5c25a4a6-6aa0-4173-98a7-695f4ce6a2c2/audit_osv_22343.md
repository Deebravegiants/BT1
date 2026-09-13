# [M] CVE-2022-2586

## Summary
Severity: Medium
Advisory: CVE-2022-2586
CVSS: 5.3 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:L/A:H)
Published: 2024-01-08
Source: https://osv.dev/vulnerability/CVE-2022-2586
Type: osv

## Details
It was discovered that a nft object or expression could reference a nft set on a different nft table, leading to a use-after-free once that table was deleted.

## References
- https://www.cisa.gov/known-exploited-vulnerabilities-catalog?field_cve=CVE-2022-2586
- https://www.vicarius.io/vsociety/posts/use-after-free-vulnerability-linked-chain-between-nft-tables-cve-2022-2586
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/2xxx/CVE-2022-2586.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-2586
- https://ubuntu.com/security/notices/USN-5557-1
- https://ubuntu.com/security/notices/USN-5560-1
- https://ubuntu.com/security/notices/USN-5560-2
- https://ubuntu.com/security/notices/USN-5562-1
- https://ubuntu.com/security/notices/USN-5564-1
- https://ubuntu.com/security/notices/USN-5565-1
- https://ubuntu.com/security/notices/USN-5566-1
- https://ubuntu.com/security/notices/USN-5567-1
- https://ubuntu.com/security/notices/USN-5582-1
- https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2022-2586
- https://lore.kernel.org/netfilter-devel/20220809170148.164591-1-cascardo@canonical.com/T/#t
- https://www.openwall.com/lists/oss-security/2022/08/09/5
- https://www.zerodayinitiative.com/advisories/ZDI-22-1118/
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git
