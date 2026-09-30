# [H] svcrdma: Address an integer overflow

## Summary
Severity: High
Advisory: CVE-2024-53151
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-12-24
Source: https://osv.dev/vulnerability/CVE-2024-53151
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.11.0 <5.15.174, >=5.16.0 <6.1.120, >=6.2.0 <6.6.64, >=6.7.0 <6.11.11, >=6.12.0 <6.12.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

svcrdma: Address an integer overflow

Dan Carpenter reports:
> Commit 78147ca8b4a9 ("svcrdma: Add a "parsed chunk list" data
> structure") from Jun 22, 2020 (linux-next), leads to the following
> Smatch static checker warning:
>
>	net/sunrpc/xprtrdma/svc_rdma_recvfrom.c:498 xdr_check_write_chunk()
>	warn: potential user controlled sizeof overflow 'segcount * 4 * 4'
>
> net/sunrpc/xprtrdma/svc_rdma_recvfrom.c
>     488 static bool xdr_check_write_chunk(struct svc_rdma_recv_ctxt *rctxt)
>     489 {
>     490         u32 segcount;
>     491         __be32 *p;
>     492
>     493         if (xdr_stream_decode_u32(&rctxt->rc_stream, &segcount))
>                                                               ^^^^^^^^
>
>     494                 return false;
>     495
>     496         /* A bogus segcount causes this buffer overflow check to fail. */
>     497         p = xdr_inline_decode(&rctxt->rc_stream,
> --> 498                               segcount * rpcrdma_segment_maxsz * sizeof(*p));
>
>
> segcount is an untrusted u32.  On 32bit systems anything >= SIZE_MAX / 16 will
> have an integer overflow and some those values will be accepted by
> xdr_inline_decode().

## References
- https://git.kernel.org/stable/c/21e1cf688fb0397788c8dd42e1e0b08d58ac5c7b
- https://git.kernel.org/stable/c/3c63d8946e578663b868cb9912dac616ea68bfd0
- https://git.kernel.org/stable/c/4cbc3ba6dc2f746497cade60bcbaa82ae3696689
- https://git.kernel.org/stable/c/838dd342962cef4c320632a5af48d3c31f2f9877
- https://git.kernel.org/stable/c/c1f8195bf68edd2cef0f18a4cead394075a54b5a
- https://git.kernel.org/stable/c/e5c440c227ecdc721f2da0dd88b6358afd1031a7
- https://lists.debian.org/debian-lts-announce/2025/03/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/53xxx/CVE-2024-53151.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-53151
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
