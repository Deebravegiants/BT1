# [C] bpf, sockmap: Don't let sock_map_{close,destroy,unhash} call itself

## Summary
Severity: Critical
Advisory: CVE-2023-52735
Ecosystem: Linux
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2023-52735
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.15.95, >=5.16.0 <6.1.13

## Details
In the Linux kernel, the following vulnerability has been resolved:

bpf, sockmap: Don't let sock_map_{close,destroy,unhash} call itself

sock_map proto callbacks should never call themselves by design. Protect
against bugs like [1] and break out of the recursive loop to avoid a stack
overflow in favor of a resource leak.

[1] https://lore.kernel.org/all/00000000000073b14905ef2e7401@google.com/

## References
- https://git.kernel.org/stable/c/5b4a79ba65a1ab479903fff2e604865d229b70a9
- https://git.kernel.org/stable/c/7499859881488da97589f3c79cc66fa75748ad49
- https://git.kernel.org/stable/c/f312367f5246e04df564d341044286e9e37a97ba
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52735.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-52735
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
