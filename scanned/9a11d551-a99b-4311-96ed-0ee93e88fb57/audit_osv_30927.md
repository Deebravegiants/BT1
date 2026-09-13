# [H] nfs/localio: must clear res.replen in nfs_local_read_done

## Summary
Severity: High
Advisory: CVE-2024-56740
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-12-29
Source: https://osv.dev/vulnerability/CVE-2024-56740
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.12.0 <6.12.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

nfs/localio: must clear res.replen in nfs_local_read_done

Otherwise memory corruption can occur due to NFSv3 LOCALIO reads
leaving garbage in res.replen:
- nfs3_read_done() copies that into server->read_hdrsize; from there
  nfs3_proc_read_setup() copies it to args.replen in new requests.
- nfs3_xdr_enc_read3args() passes that to rpc_prepare_reply_pages()
  which includes it in hdrsize for xdr_init_pages, so that rq_rcv_buf
  contains a ridiculous len.
- This is copied to rq_private_buf and xs_read_stream_request()
  eventually passes the kvec to sock_recvmsg() which receives incoming
  data into entirely the wrong place.

This is easily reproduced with NFSv3 LOCALIO that is servicing reads
when it is made to pivot back to using normal RPC.  This switch back
to using normal NFSv3 with RPC can occur for a few reasons but this
issue was exposed with a test that stops and then restarts the NFSv3
server while LOCALIO is performing heavy read IO.

## References
- https://git.kernel.org/stable/c/650703bc4ed3edf841e851c99ab8e7ba9e5262a3
- https://git.kernel.org/stable/c/de5dac261eeab99762bbdf7c20cee5d26ef4462e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/56xxx/CVE-2024-56740.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-56740
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
