# [H] RDMA/siw: Fix connection failure handling

## Summary
Severity: High
Advisory: CVE-2023-52513
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-03-02
Source: https://osv.dev/vulnerability/CVE-2023-52513
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.3.0 <5.4.258, >=5.5.0 <5.10.198, >=5.11.0 <5.15.135, >=5.16.0 <6.1.57, >=6.2.0 <6.5.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

RDMA/siw: Fix connection failure handling

In case immediate MPA request processing fails, the newly
created endpoint unlinks the listening endpoint and is
ready to be dropped. This special case was not handled
correctly by the code handling the later TCP socket close,
causing a NULL dereference crash in siw_cm_work_handler()
when dereferencing a NULL listener. We now also cancel
the useless MPA timeout, if immediate MPA request
processing fails.

This patch furthermore simplifies MPA processing in general:
Scheduling a useless TCP socket read in sk_data_ready() upcall
is now surpressed, if the socket is already moved out of
TCP_ESTABLISHED state.

## References
- https://git.kernel.org/stable/c/0d520cdb0cd095eac5d00078dfd318408c9b5eed
- https://git.kernel.org/stable/c/53a3f777049771496f791504e7dc8ef017cba590
- https://git.kernel.org/stable/c/5cf38e638e5d01b68f9133968a85e8b3fd1ecf2f
- https://git.kernel.org/stable/c/6e26812e289b374c17677d238164a5a8f5770594
- https://git.kernel.org/stable/c/81b7bf367eea795d259d0261710c6a89f548844d
- https://git.kernel.org/stable/c/eeafc50a77f6a783c2c44e7ec3674a7b693e06f8
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52513.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-52513
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
