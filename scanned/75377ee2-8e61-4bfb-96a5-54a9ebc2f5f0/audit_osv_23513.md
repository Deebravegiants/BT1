# [H] libbpf: Handle size overflow for ringbuf mmap

## Summary
Severity: High
Advisory: CVE-2022-49030
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-10-21
Source: https://osv.dev/vulnerability/CVE-2022-49030
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.8.0 <5.10.158, >=5.11.0 <5.15.82, >=5.16.0 <6.0.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

libbpf: Handle size overflow for ringbuf mmap

The maximum size of ringbuf is 2GB on x86-64 host, so 2 * max_entries
will overflow u32 when mapping producer page and data pages. Only
casting max_entries to size_t is not enough, because for 32-bits
application on 64-bits kernel the size of read-only mmap region
also could overflow size_t.

So fixing it by casting the size of read-only mmap region into a __u64
and checking whether or not there will be overflow during mmap.

## References
- https://git.kernel.org/stable/c/0140e079a42064680394fff1199a7b5483688dec
- https://git.kernel.org/stable/c/535a25ab4f9a45f74ba38ab71de95e97474922ed
- https://git.kernel.org/stable/c/8a549ab6724520aa3c07f47e0eba820293551490
- https://git.kernel.org/stable/c/927cbb478adf917e0a142b94baa37f06279cc466
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49030.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49030
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
