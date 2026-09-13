# [M] CVE-2022-2588

## Summary
Severity: Medium
Advisory: CVE-2022-2588
CVSS: 5.3 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:L/A:H)
Published: 2024-01-08
Source: https://osv.dev/vulnerability/CVE-2022-2588
Type: osv

## Details
It was discovered that the cls_route filter implementation in the Linux kernel would not remove an old filter from the hashtable before freeing it if its handle had the value 0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/2xxx/CVE-2022-2588.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-2588
- https://ubuntu.com/security/notices/USN-5557-1
- https://ubuntu.com/security/notices/USN-5560-1
- https://ubuntu.com/security/notices/USN-5560-2
- https://ubuntu.com/security/notices/USN-5562-1
- https://ubuntu.com/security/notices/USN-5564-1
- https://ubuntu.com/security/notices/USN-5565-1
- https://ubuntu.com/security/notices/USN-5566-1
- https://ubuntu.com/security/notices/USN-5567-1
- https://ubuntu.com/security/notices/USN-5582-1
- https://ubuntu.com/security/notices/USN-5588-1
- https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2022-2588
- https://github.com/Markakd/CVE-2022-2588
- https://lore.kernel.org/netdev/20220809170518.164662-1-cascardo@canonical.com/T/#u
- https://www.openwall.com/lists/oss-security/2022/08/09/6
- https://www.zerodayinitiative.com/advisories/ZDI-22-1117/
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git
