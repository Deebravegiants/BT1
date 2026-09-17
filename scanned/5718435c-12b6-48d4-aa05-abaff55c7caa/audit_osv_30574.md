# [H] NFSv4.0: Fix a use-after-free problem in the asynchronous open()

## Summary
Severity: High
Advisory: CVE-2024-53173
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-12-27
Source: https://osv.dev/vulnerability/CVE-2024-53173
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.16 <4.19.325, >=4.20.0 <5.4.287, >=5.5.0 <5.10.231, >=5.11.0 <5.15.174, >=5.16.0 <6.1.120, >=6.2.0 <6.6.64, >=6.7.0 <6.11.11, >=6.12.0 <6.12.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

NFSv4.0: Fix a use-after-free problem in the asynchronous open()

Yang Erkun reports that when two threads are opening files at the same
time, and are forced to abort before a reply is seen, then the call to
nfs_release_seqid() in nfs4_opendata_free() can result in a
use-after-free of the pointer to the defunct rpc task of the other
thread.
The fix is to ensure that if the RPC call is aborted before the call to
nfs_wait_on_sequence() is complete, then we must call nfs_release_seqid()
in nfs4_open_release() before the rpc_task is freed.

## References
- https://git.kernel.org/stable/c/1cfae9575296f5040cdc84b0730e79078c081d2d
- https://git.kernel.org/stable/c/229a30ed42bb87bcb044c5523fabd9e4f0e75648
- https://git.kernel.org/stable/c/2ab9639f16b05d948066a6c4cf19a0fdc61046ff
- https://git.kernel.org/stable/c/2fdb05dc0931250574f0cb0ebeb5ed8e20f4a889
- https://git.kernel.org/stable/c/5237a297ffd374a1c4157a53543b7a69d7bbbc03
- https://git.kernel.org/stable/c/7bf6bf130af8ee7d93a99c28a7512df3017ec759
- https://git.kernel.org/stable/c/b56ae8e715557b4fc227c9381d2e681ffafe7b15
- https://git.kernel.org/stable/c/ba6e6c04f60fe52d91520ac4d749d372d4c74521
- https://git.kernel.org/stable/c/e2277a1d9d5cd0d625a4fd7c04fce2b53e66df77
- https://lists.debian.org/debian-lts-announce/2025/03/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/53xxx/CVE-2024-53173.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-53173
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
