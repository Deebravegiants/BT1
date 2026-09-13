# [H] netlink: terminate outstanding dump on socket close

## Summary
Severity: High
Advisory: CVE-2024-53140
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-12-04
Source: https://osv.dev/vulnerability/CVE-2024-53140
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.9.0 <4.19.325, >=4.20.0 <5.4.287, >=5.5.0 <5.10.231, >=5.11.0 <5.15.174, >=5.16.0 <6.1.119, >=6.2.0 <6.6.63, >=6.7.0 <6.11.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

netlink: terminate outstanding dump on socket close

Netlink supports iterative dumping of data. It provides the families
the following ops:
 - start - (optional) kicks off the dumping process
 - dump  - actual dump helper, keeps getting called until it returns 0
 - done  - (optional) pairs with .start, can be used for cleanup
The whole process is asynchronous and the repeated calls to .dump
don't actually happen in a tight loop, but rather are triggered
in response to recvmsg() on the socket.

This gives the user full control over the dump, but also means that
the user can close the socket without getting to the end of the dump.
To make sure .start is always paired with .done we check if there
is an ongoing dump before freeing the socket, and if so call .done.

The complication is that sockets can get freed from BH and .done
is allowed to sleep. So we use a workqueue to defer the call, when
needed.

Unfortunately this does not work correctly. What we defer is not
the cleanup but rather releasing a reference on the socket.
We have no guarantee that we own the last reference, if someone
else holds the socket they may release it in BH and we're back
to square one.

The whole dance, however, appears to be unnecessary. Only the user
can interact with dumps, so we can clean up when socket is closed.
And close always happens in process context. Some async code may
still access the socket after close, queue notification skbs to it etc.
but no dumps can start, end or otherwise make progress.

Delete the workqueue and flush the dump state directly from the release
handler. Note that further cleanup is possible in -next, for instance
we now always call .done before releasing the main module reference,
so dump doesn't have to take a reference of its own.

## References
- https://git.kernel.org/stable/c/114a61d8d94ae3a43b82446cf737fd757021b834
- https://git.kernel.org/stable/c/176c41b3ca9281a9736b67c6121b03dbf0c8c08f
- https://git.kernel.org/stable/c/1904fb9ebf911441f90a68e96b22aa73e4410505
- https://git.kernel.org/stable/c/4e87a52133284afbd40fb522dbf96e258af52a98
- https://git.kernel.org/stable/c/598c956b62699c3753929602560d8df322e60559
- https://git.kernel.org/stable/c/6e3f2c512d2b7dbd247485b1dd9e43e4210a18f4
- https://git.kernel.org/stable/c/bbc769d2fa1b8b368c5fbe013b5b096afa3c05ca
- https://git.kernel.org/stable/c/d2fab3d66cc16cfb9e3ea1772abe6b79b71fa603
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/53xxx/CVE-2024-53140.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-53140
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
