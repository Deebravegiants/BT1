# [H] NFSD: Fix the behavior of READ near OFFSET_MAX

## Summary
Severity: High
Advisory: CVE-2022-48827
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-07-16
Source: https://osv.dev/vulnerability/CVE-2022-48827
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.12 <5.10.220, >=5.11.0 <5.15.24, >=5.16.0 <5.16.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

NFSD: Fix the behavior of READ near OFFSET_MAX

Dan Aloni reports:
> Due to commit 8cfb9015280d ("NFS: Always provide aligned buffers to
> the RPC read layers") on the client, a read of 0xfff is aligned up
> to server rsize of 0x1000.
>
> As a result, in a test where the server has a file of size
> 0x7fffffffffffffff, and the client tries to read from the offset
> 0x7ffffffffffff000, the read causes loff_t overflow in the server
> and it returns an NFS code of EINVAL to the client. The client as
> a result indefinitely retries the request.

The Linux NFS client does not handle NFS?ERR_INVAL, even though all
NFS specifications permit servers to return that status code for a
READ.

Instead of NFS?ERR_INVAL, have out-of-range READ requests succeed
and return a short result. Set the EOF flag in the result to prevent
the client from retrying the READ request. This behavior appears to
be consistent with Solaris NFS servers.

Note that NFSv3 and NFSv4 use u64 offset values on the wire. These
must be converted to loff_t internally before use -- an implicit
type cast is not adequate for this purpose. Otherwise VFS checks
against sb->s_maxbytes do not work properly.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-265688.html
- https://cert-portal.siemens.com/productcert/html/ssa-355557.html
- https://git.kernel.org/stable/c/0cb4d23ae08c48f6bf3c29a8e5c4a74b8388b960
- https://git.kernel.org/stable/c/1726a39b0879acfb490b22dca643f26f4f907da9
- https://git.kernel.org/stable/c/44502aca8e02ab32d6b0eb52e006a5ec9402719b
- https://git.kernel.org/stable/c/c6eff5c4277146a78b4fb8c9b668dd64542c41b0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/48xxx/CVE-2022-48827.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-48827
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
