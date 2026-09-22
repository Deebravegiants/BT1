# [H] wifi: mac80211: check S1G action frame size

## Summary
Severity: High
Advisory: CVE-2023-53257
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:H)
Published: 2025-09-15
Source: https://osv.dev/vulnerability/CVE-2023-53257
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <5.15.133, >=5.16.0 <6.1.55, >=6.2.0 <6.5.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: mac80211: check S1G action frame size

Before checking the action code, check that it even
exists in the frame.

## References
- https://git.kernel.org/stable/c/19e4a47ee74718a22e963e8a647c8c3bfe8bb05c
- https://git.kernel.org/stable/c/5e030a2509be72b452b6f4a800786d43229414db
- https://git.kernel.org/stable/c/7ae7a1378a119780c8c17a6b5fc03011c3bb7029
- https://git.kernel.org/stable/c/fedd9377dd9c71a950d432fbe1628eebfbed70a1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53257.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53257
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
