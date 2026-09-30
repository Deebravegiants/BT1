# [H] ksmbd: fix use-after-free in ksmbd_session_rpc_open

## Summary
Severity: High
Advisory: CVE-2025-37926
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-05-20
Source: https://osv.dev/vulnerability/CVE-2025-37926
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <6.1.162, >=6.2.0 <6.6.122, >=6.7.0 <6.12.28, >=6.13.0 <6.14.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

ksmbd: fix use-after-free in ksmbd_session_rpc_open

A UAF issue can occur due to a race condition between
ksmbd_session_rpc_open() and __session_rpc_close().
Add rpc_lock to the session to protect it.

## References
- https://git.kernel.org/stable/c/1067361a1cc6ad9cdf7acfc47f90012b72ad1502
- https://git.kernel.org/stable/c/6323fec65fe54b365961fed260dd579191e46121
- https://git.kernel.org/stable/c/8fb3b6c85b7e3127161623586b62abcc366caa20
- https://git.kernel.org/stable/c/a1f46c99d9ea411f9bf30025b912d881d36fc709
- https://git.kernel.org/stable/c/a4348710a7267705b75692dc1a000920481d1d92
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/37xxx/CVE-2025-37926.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-37926
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
