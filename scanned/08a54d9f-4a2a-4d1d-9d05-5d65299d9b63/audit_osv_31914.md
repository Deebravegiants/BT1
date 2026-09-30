# [H] wifi: cfg80211: cancel wiphy_work before freeing wiphy

## Summary
Severity: High
Advisory: CVE-2025-21979
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-04-01
Source: https://osv.dev/vulnerability/CVE-2025-21979
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.1.132, >=6.2.0 <6.6.84, >=6.5.0 <6.12.20, >=6.7.0 <6.13.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: cfg80211: cancel wiphy_work before freeing wiphy

A wiphy_work can be queued from the moment the wiphy is allocated and
initialized (i.e. wiphy_new_nm). When a wiphy_work is queued, the
rdev::wiphy_work is getting queued.

If wiphy_free is called before the rdev::wiphy_work had a chance to run,
the wiphy memory will be freed, and then when it eventally gets to run
it'll use invalid memory.

Fix this by canceling the work before freeing the wiphy.

## References
- https://git.kernel.org/stable/c/0272d4af7f92997541d8bbf4c51918b93ded6ee2
- https://git.kernel.org/stable/c/72d520476a2fab6f3489e8388ab524985d6c4b90
- https://git.kernel.org/stable/c/75d262ad3c36d52852d764588fcd887f0fcd9138
- https://git.kernel.org/stable/c/8930a3e1568cf534f86c8ed2def817c6d0528fc1
- https://git.kernel.org/stable/c/a5158d67bff06cb6fea31be39aeb319fd908ed8e
- https://git.kernel.org/stable/c/dea22de162058216a90f2706f0d0b36f0ff309fd
- https://lists.debian.org/debian-lts-announce/2025/05/msg00045.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21979.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21979
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
