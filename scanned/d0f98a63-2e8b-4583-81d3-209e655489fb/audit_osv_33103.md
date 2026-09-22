# [C] tls: fix handling of zero-length records on the rx_list

## Summary
Severity: Critical
Advisory: CVE-2025-39682
Aliases: A-440544511, ASB-A-440544511
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-09-05
Source: https://osv.dev/vulnerability/CVE-2025-39682
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.0.0 <6.1.149, >=6.2.0 <6.6.103, >=6.7.0 <6.12.44, >=6.13.0 <6.16.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

tls: fix handling of zero-length records on the rx_list

Each recvmsg() call must process either
 - only contiguous DATA records (any number of them)
 - one non-DATA record

If the next record has different type than what has already been
processed we break out of the main processing loop. If the record
has already been decrypted (which may be the case for TLS 1.3 where
we don't know type until decryption) we queue the pending record
to the rx_list. Next recvmsg() will pick it up from there.

Queuing the skb to rx_list after zero-copy decrypt is not possible,
since in that case we decrypted directly to the user space buffer,
and we don't have an skb to queue (darg.skb points to the ciphertext
skb for access to metadata like length).

Only data records are allowed zero-copy, and we break the processing
loop after each non-data record. So we should never zero-copy and
then find out that the record type has changed. The corner case
we missed is when the initial record comes from rx_list, and it's
zero length.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-032379.html
- https://git.kernel.org/stable/c/2902c3ebcca52ca845c03182000e8d71d3a5196f
- https://git.kernel.org/stable/c/29c0ce3c8cdb6dc5d61139c937f34cb888a6f42e
- https://git.kernel.org/stable/c/3439c15ae91a517cf3c650ea15a8987699416ad9
- https://git.kernel.org/stable/c/62708b9452f8eb77513115b17c4f8d1a22ebf843
- https://git.kernel.org/stable/c/c09dd3773b5950e9cfb6c9b9a5f6e36d06c62677
- https://lists.debian.org/debian-lts-announce/2025/10/msg00008.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/39xxx/CVE-2025-39682.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-39682
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
