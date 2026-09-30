# [H] wifi: iwlwifi: mvm: don't read past the mfuart notifcation

## Summary
Severity: High
Advisory: CVE-2024-40941
Ecosystem: Linux
CVSS: 8.1 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2024-07-12
Source: https://osv.dev/vulnerability/CVE-2024-40941
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.12.0 <4.19.317, >=4.20.0 <5.4.279, >=5.5.0 <5.10.221, >=5.11.0 <5.15.162, >=5.16.0 <6.1.95, >=6.2.0 <6.6.35, >=6.7.0 <6.9.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: iwlwifi: mvm: don't read past the mfuart notifcation

In case the firmware sends a notification that claims it has more data
than it has, we will read past that was allocated for the notification.
Remove the print of the buffer, we won't see it by default. If needed,
we can see the content with tracing.

This was reported by KFENCE.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-265688.html
- https://cert-portal.siemens.com/productcert/html/ssa-355557.html
- https://git.kernel.org/stable/c/15b37c6fab9d5e40ac399fa1c725118588ed649c
- https://git.kernel.org/stable/c/46c59a25337049a2a230ce7f7c3b9f21d0aaaad7
- https://git.kernel.org/stable/c/4bb95f4535489ed830cf9b34b0a891e384d1aee4
- https://git.kernel.org/stable/c/6532f18e66b384b8d4b7e5c9caca042faaa9e8de
- https://git.kernel.org/stable/c/65686118845d427df27ee83a6ddd4885596b0805
- https://git.kernel.org/stable/c/a05018739a5e6b9dc112c95bd4c59904062c8940
- https://git.kernel.org/stable/c/a8bc8276af9aeacabb773f0c267cfcdb847c6f2d
- https://git.kernel.org/stable/c/acdfa33c3cf5e1cd185cc1e0486bd0ea9f09c154
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/40xxx/CVE-2024-40941.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-40941
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
