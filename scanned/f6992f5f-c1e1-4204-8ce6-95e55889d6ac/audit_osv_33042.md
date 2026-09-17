# [H] bpf, ktls: Fix data corruption when using bpf_msg_pop_data() in ktls

## Summary
Severity: High
Advisory: CVE-2025-38608
Ecosystem: Linux
CVSS: 8.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:L)
Published: 2025-08-19
Source: https://osv.dev/vulnerability/CVE-2025-38608
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.0.0 <5.4.297, >=5.5.0 <5.10.241, >=5.11.0 <5.15.190, >=5.16.0 <6.1.148, >=6.2.0 <6.6.102, >=6.7.0 <6.12.42, >=6.13.0 <6.15.10, >=6.16.0 <6.16.1

## Details
In the Linux kernel, the following vulnerability has been resolved:

bpf, ktls: Fix data corruption when using bpf_msg_pop_data() in ktls

When sending plaintext data, we initially calculated the corresponding
ciphertext length. However, if we later reduced the plaintext data length
via socket policy, we failed to recalculate the ciphertext length.

This results in transmitting buffers containing uninitialized data during
ciphertext transmission.

This causes uninitialized bytes to be appended after a complete
"Application Data" packet, leading to errors on the receiving end when
parsing TLS record.

## References
- https://git.kernel.org/stable/c/0e853c1464bcf61207f8b5c32d2ac5ee495e859d
- https://git.kernel.org/stable/c/16aca8bb4ad0d8a13c8b6da4007f4e52d53035bb
- https://git.kernel.org/stable/c/178f6a5c8cb3b6be1602de0964cd440243f493c9
- https://git.kernel.org/stable/c/1e480387d4b42776f8957fb148af9d75ce93b96d
- https://git.kernel.org/stable/c/6ba20ff3cdb96a908b9dc93cf247d0b087672e7c
- https://git.kernel.org/stable/c/73fc5d04009d3969ff8e8574f0fd769f04124e59
- https://git.kernel.org/stable/c/849d24dc5aed45ebeb3490df429356739256ac40
- https://git.kernel.org/stable/c/90d6ef67440cec2a0aad71a0108c8f216437345c
- https://git.kernel.org/stable/c/ee03766d79de0f61ea29ffb6ab1c7b196ea1b02e
- https://lists.debian.org/debian-lts-announce/2025/10/msg00007.html
- https://lists.debian.org/debian-lts-announce/2025/10/msg00008.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38608.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38608
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
