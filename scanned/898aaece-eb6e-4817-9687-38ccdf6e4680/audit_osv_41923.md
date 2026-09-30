# [C] RDMA/siw: Reject MPA FPDU length underflow before signed receive math

## Summary
Severity: Critical
Advisory: CVE-2026-64102
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-64102
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.3.0 <5.10.258, >=5.11.0 <5.15.209, >=5.16.0 <6.1.175, >=6.2.0 <6.6.142, >=6.7.0 <6.12.92, >=6.13.0 <6.18.34, >=6.19.0 <7.0.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

RDMA/siw: Reject MPA FPDU length underflow before signed receive math

A malicious connected siw peer can send an iWARP FPDU whose MPA length
field (c_hdr->mpa_len, 16 bit big-endian, peer-controlled) is smaller
than the fixed DDP/RDMAP header for the announced opcode. Soft-iWARP
parses the full header in siw_get_hdr() based on iwarp_pktinfo[opcode]
.hdr_len, but never compares mpa_len against that header length.

siw_tcp_rx_data() then derives

    srx->fpdu_part_rem = be16_to_cpu(mpa_len) - fpdu_part_rcvd
                         + MPA_HDR_SIZE;

where fpdu_part_rcvd equals iwarp_pktinfo[opcode].hdr_len at this
point. For a tagged WRITE (hdr_len 16, MPA_HDR_SIZE 2) the smallest
on-wire mpa_len of 0 yields fpdu_part_rem = -14, and any mpa_len below
hdr_len - MPA_HDR_SIZE underflows to a negative int.

The signed value then flows into siw_proc_write()/siw_proc_rresp() as

    bytes = min(srx->fpdu_part_rem, srx->skb_new);

is handed to siw_check_mem() as an int len (whose interval check
addr + len > mem->va + mem->len is satisfied for a valid base when
len is negative), and reaches siw_rx_data() -> siw_rx_kva() /
siw_rx_umem() -> skb_copy_bits() as a signed copy length. The header
copy branch in skb_copy_bits() promotes that to size_t, producing a
multi-gigabyte read.

KASAN under a KUnit harness that drives the real kernel TCP receive
path -- a loopback AF_INET socketpair, the malformed FPDU written via
kernel_sendmsg, sk_data_ready firing in softirq, tcp_read_sock
dispatching to siw_tcp_rx_data -- reports:

    BUG: KASAN: use-after-free in skb_copy_bits+0x284/0x480
    Read of size 4294967295 at addr ffff888...
    Call Trace:
     skb_copy_bits
     siw_rx_kva
     siw_rx_data
     siw_check_mem
     siw_proc_write
     siw_tcp_rx_data
     __tcp_read_sock
     siw_qp_llp_data_ready
     tcp_data_ready
     tcp_data_queue

Add the missing invariant at the earliest point where the peer header
is fully assembled. iwarp_pktinfo[*].hdr_len - MPA_HDR_SIZE is exactly
the value the siw transmitter uses as the minimum mpa_len for each
opcode (drivers/infiniband/sw/siw/siw_qp.c:33), so this matches the
protocol contract. Out-of-range FPDUs terminate the connection with
TERM_ERROR_LAYER_LLP / LLP_ETYPE_MPA / LLP_ECODE_FPDU_START -- which
is RFC 5044 Section 8 error code 3 ("Marker and ULPDU Length fields
do not agree on the start of an FPDU"), the correct framing-error
class for this inconsistency.

## References
- https://git.kernel.org/stable/c/0ce1bc9e46ecabe84772bb561e373c0d9876d6f2
- https://git.kernel.org/stable/c/1012896f4225e8f801ff3c1648023845b66dfb11
- https://git.kernel.org/stable/c/14553be882d9ce91749c9d64041de66e34ad8e70
- https://git.kernel.org/stable/c/33a8b5e971e294ec2a7b74211c545e09efd8e9ac
- https://git.kernel.org/stable/c/4a331582011d9e8089af8aa2a61ec6b4443bb245
- https://git.kernel.org/stable/c/683f7cfbf514193d63c0efa079f3352bde84c2e0
- https://git.kernel.org/stable/c/775b4dc9618a99a1fa48b57554041a5dc17e1336
- https://git.kernel.org/stable/c/c7c0c0f4379dedec12d24dbb9dded5d2db7fd9f2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64102.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64102
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
