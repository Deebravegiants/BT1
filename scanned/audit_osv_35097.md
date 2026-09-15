# [C] libceph: prevent potential out-of-bounds writes in handle_auth_session_key()

## Summary
Severity: Critical
Advisory: CVE-2025-68284
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-16
Source: https://osv.dev/vulnerability/CVE-2025-68284
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.11.0 <5.15.197, >=5.16.0 <6.1.159, >=6.2.0 <6.6.119, >=6.7.0 <6.12.61, >=6.13.0 <6.17.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

libceph: prevent potential out-of-bounds writes in handle_auth_session_key()

The len field originates from untrusted network packets. Boundary
checks have been added to prevent potential out-of-bounds writes when
decrypting the connection secret or processing service tickets.

[ idryomov: changelog ]

## References
- https://git.kernel.org/stable/c/5ef575834ca99f719d7573cdece9df2fe2b72424
- https://git.kernel.org/stable/c/6920ff09bf911bc919cd7a6b7176fbdd1a6e6850
- https://git.kernel.org/stable/c/7fce830ecd0a0256590ee37eb65a39cbad3d64fc
- https://git.kernel.org/stable/c/8dfcc56af28cffb8f25fb9be37b3acc61f2a3d09
- https://git.kernel.org/stable/c/ccbccfba25e9aa395daaea156b5e7790910054c4
- https://git.kernel.org/stable/c/f22c55a20a2d9ffbbac57408d5d488cef8201e9d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/68xxx/CVE-2025-68284.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-68284
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
