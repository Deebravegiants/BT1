# [M] tcp: Fix data-races around sysctl_tcp_fastopen.

## Summary
Severity: Medium
Advisory: CVE-2022-49586
Ecosystem: Linux
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49586
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.6.0 <4.19.254, >=4.20.0 <5.4.208, >=5.5.0 <5.10.134, >=5.11.0 <5.15.58, >=5.16.0 <5.18.15

## Details
In the Linux kernel, the following vulnerability has been resolved:

tcp: Fix data-races around sysctl_tcp_fastopen.

While reading sysctl_tcp_fastopen, it can be changed concurrently.
Thus, we need to add READ_ONCE() to its readers.

## References
- https://git.kernel.org/stable/c/03da610696a32578fc4f986479341ce9d430df08
- https://git.kernel.org/stable/c/22938534c611136f35e2ca545bb668073ca5ef49
- https://git.kernel.org/stable/c/25d53d858a6c0b89a6e69e376c2a57c4f4c2c8cc
- https://git.kernel.org/stable/c/448ab998947996a0a451f8229f19087964cf2670
- https://git.kernel.org/stable/c/539d9ab79eba3974b479cad61a8688c41fe62e12
- https://git.kernel.org/stable/c/5a54213318c43f4009ae158347aa6016e3b9b55a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49586.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49586
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
