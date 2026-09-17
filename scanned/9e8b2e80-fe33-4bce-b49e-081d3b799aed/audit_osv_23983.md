# [C] ceph: avoid putting the realm twice when decoding snaps fails

## Summary
Severity: Critical
Advisory: CVE-2022-49770
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-05-01
Source: https://osv.dev/vulnerability/CVE-2022-49770
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.0.0 <4.19.268, >=4.20.0 <5.4.226, >=5.5.0 <5.10.157, >=5.11.0 <5.15.81, >=5.16.0 <6.0.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

ceph: avoid putting the realm twice when decoding snaps fails

When decoding the snaps fails it maybe leaving the 'first_realm'
and 'realm' pointing to the same snaprealm memory. And then it'll
put it twice and could cause random use-after-free, BUG_ON, etc
issues.

## References
- https://git.kernel.org/stable/c/044bc6d3c2c0e9090b0841e7b723875756534b45
- https://git.kernel.org/stable/c/274e4c79a3a2a24fba7cfe0e41113f1138785c37
- https://git.kernel.org/stable/c/2f6e2de3a5289004650118b61f138fe7c28e1905
- https://git.kernel.org/stable/c/51884d153f7ec85e18d607b2467820a90e0f4359
- https://git.kernel.org/stable/c/cb7495fe957526555782ce0723f79ce92a6db22e
- https://git.kernel.org/stable/c/fd879c83e87735ab8f00ef7755752cf0cbae24b2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49770.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49770
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
