# [M] ipv6: sr: fix missing sk_buff release in seg6_input_core

## Summary
Severity: Medium
Advisory: CVE-2024-39490
Ecosystem: Linux
CVSS: 6.2 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2024-07-10
Source: https://osv.dev/vulnerability/CVE-2024-39490
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.12.0 <5.15.161, >=5.16.0 <6.1.93, >=6.2.0 <6.6.33, >=6.7.0 <6.9.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

ipv6: sr: fix missing sk_buff release in seg6_input_core

The seg6_input() function is responsible for adding the SRH into a
packet, delegating the operation to the seg6_input_core(). This function
uses the skb_cow_head() to ensure that there is sufficient headroom in
the sk_buff for accommodating the link-layer header.
In the event that the skb_cow_header() function fails, the
seg6_input_core() catches the error but it does not release the sk_buff,
which will result in a memory leak.

This issue was introduced in commit af3b5158b89d ("ipv6: sr: fix BUG due
to headroom too small after SRH push") and persists even after commit
7a3f5b0de364 ("netfilter: add netfilter hooks to SRv6 data plane"),
where the entire seg6_input() code was refactored to deal with netfilter
hooks.

The proposed patch addresses the identified memory leak by requiring the
seg6_input_core() function to release the sk_buff in the event that
skb_cow_head() fails.

## References
- https://git.kernel.org/stable/c/5447f9708d9e4c17a647b16a9cb29e9e02820bd9
- https://git.kernel.org/stable/c/8f1fc3b86eaea70be6abcae2e9aa7e7b99453864
- https://git.kernel.org/stable/c/e8688218e38111ace457509d8f0cad75f79c1a7a
- https://git.kernel.org/stable/c/f4df8c7670a73752201cbde215254598efdf6ce8
- https://git.kernel.org/stable/c/f5fec1588642e415a3d72e02140160661b303940
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/39xxx/CVE-2024-39490.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-39490
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
