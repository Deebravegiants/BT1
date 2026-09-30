# [H] bpf, sockmap: Several fixes to bpf_msg_pop_data

## Summary
Severity: High
Advisory: CVE-2024-56720
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-12-29
Source: https://osv.dev/vulnerability/CVE-2024-56720
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.0.0 <5.4.287, >=5.5.0 <5.10.231, >=5.11.0 <5.15.174, >=5.16.0 <6.1.120, >=6.2.0 <6.6.64, >=6.7.0 <6.11.11, >=6.12.0 <6.12.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

bpf, sockmap: Several fixes to bpf_msg_pop_data

Several fixes to bpf_msg_pop_data,
1. In sk_msg_shift_left, we should put_page
2. if (len == 0), return early is better
3. pop the entire sk_msg (last == msg->sg.size) should be supported
4. Fix for the value of variable "a"
5. In sk_msg_shift_left, after shifting, i has already pointed to the next
element. Addtional sk_msg_iter_var_next may result in BUG.

## References
- https://git.kernel.org/stable/c/275a9f3ef8fabb0cb282a62b9e164dedba7284c5
- https://git.kernel.org/stable/c/5d609ba262475db450ba69b8e8a557bd768ac07a
- https://git.kernel.org/stable/c/785180bed9879680d8e5c5e1b54c8ae8d948f4c8
- https://git.kernel.org/stable/c/98c7ea7d11f2588e8197db042e0291e4ac8f8346
- https://git.kernel.org/stable/c/d26d977633d1d0b8bf9407278189bd0a8d973323
- https://git.kernel.org/stable/c/d3f5763b3062514a234114e97bbde74d8d702449
- https://git.kernel.org/stable/c/e1f54c61c4c9a5244eb8159dce60d248f7d97b32
- https://git.kernel.org/stable/c/f58d3aa457e77a3d9b3df2ab081dcf9950f6029f
- https://lists.debian.org/debian-lts-announce/2025/03/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/56xxx/CVE-2024-56720.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-56720
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
