# [M] CVE-2022-2585

## Summary
Severity: Medium
Advisory: CVE-2022-2585
CVSS: 5.3 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:L/A:H)
Published: 2024-01-08
Source: https://osv.dev/vulnerability/CVE-2022-2585
Type: osv

## Details
It was discovered that when exec'ing from a non-leader thread, armed POSIX CPU timers would be left on a list but freed, leading to a use-after-free.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/2xxx/CVE-2022-2585.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-2585
- https://ubuntu.com/security/notices/USN-5564-1
- https://ubuntu.com/security/notices/USN-5565-1
- https://ubuntu.com/security/notices/USN-5566-1
- https://ubuntu.com/security/notices/USN-5567-1
- https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2022-2585
- https://lore.kernel.org/lkml/20220809170751.164716-1-cascardo@canonical.com/T/#u
- https://www.openwall.com/lists/oss-security/2022/08/09/7
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git
