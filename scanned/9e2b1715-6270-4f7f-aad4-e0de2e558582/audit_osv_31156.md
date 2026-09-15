# [C] ksmbd: fix racy issue from session lookup and expire

## Summary
Severity: Critical
Advisory: CVE-2024-58087
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-03-12
Source: https://osv.dev/vulnerability/CVE-2024-58087
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <5.15.176, >=5.16.0 <6.1.121, >=6.2.0 <6.6.67, >=6.7.0 <6.12.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

ksmbd: fix racy issue from session lookup and expire

Increment the session reference count within the lock for lookup to avoid
racy issue with session expire.

## References
- https://git.kernel.org/stable/c/2107ab40629aeabbec369cf34b8cf0f288c3eb1b
- https://git.kernel.org/stable/c/37a0e2b362b3150317fb6e2139de67b1e29ae5ff
- https://git.kernel.org/stable/c/450a844c045ff0895d41b05a1cbe8febd1acfcfd
- https://git.kernel.org/stable/c/a39e31e22a535d47b14656a7d6a893c7f6cf758c
- https://git.kernel.org/stable/c/b95629435b84b9ecc0c765995204a4d8a913ed52
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/58xxx/CVE-2024-58087.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-58087
- https://www.zerodayinitiative.com/advisories/ZDI-25-100/
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
