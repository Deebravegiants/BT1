# [H] can: j1939: transport: j1939_session_fresh_new(): initialize receive buffer

## Summary
Severity: High
Advisory: CVE-2026-80707
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-08-28
Source: https://osv.dev/vulnerability/CVE-2026-80707
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.4.0 <5.10.265, >=5.11.0 <5.15.216, >=5.16.0 <6.1.183, >=6.2.0 <6.6.151, >=6.7.0 <6.12.103, >=6.13.0 <6.18.44, >=6.19.0 <7.1.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

can: j1939: transport: j1939_session_fresh_new(): initialize receive buffer

Zero the allocated buffer in j1939_session_fresh_new() to ensure it
contains no residual data.

While there is a potential performance impact if users allocate maximum
sized ETP buffers, most real-world use cases are not noticeably affected
since the maximum known buffer size is typically around 65K.

[mkl: add Message-ID]

## References
- https://git.kernel.org/stable/c/038bad8e16c2e28acf31f0b527a816fb23a57269
- https://git.kernel.org/stable/c/194d67e92197eb820f4c2c6605d9721333b3eba0
- https://git.kernel.org/stable/c/348818277a3646d5b9fa60c9d20c00dc4bc86832
- https://git.kernel.org/stable/c/8604a3b81b9d0ceaf04fee5f52e701f623a179f9
- https://git.kernel.org/stable/c/bbfa49d1e287de44994955b44d19281be3195b44
- https://git.kernel.org/stable/c/d5b3613c7d69d8dcb4dd6704f1f463198ce9f6cf
- https://git.kernel.org/stable/c/eb96c58907922546e415e545fe9a14ea63b02719
- https://git.kernel.org/stable/c/f3e120a34b336079479fa10f706f0636eaa6e751
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/80xxx/CVE-2026-80707.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-80707
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
