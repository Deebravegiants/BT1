# [H] io_uring/af_unix: disable sending io_uring over sockets

## Summary
Severity: High
Advisory: CVE-2023-52654
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-09
Source: https://osv.dev/vulnerability/CVE-2023-52654
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.4.264, >=5.5.0 <5.10.204, >=5.11.0 <5.15.143, >=5.16.0 <6.1.68, >=6.1.0 <6.6.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

io_uring/af_unix: disable sending io_uring over sockets

File reference cycles have caused lots of problems for io_uring
in the past, and it still doesn't work exactly right and races with
unix_stream_read_generic(). The safest fix would be to completely
disallow sending io_uring files via sockets via SCM_RIGHT, so there
are no possible cycles invloving registered files and thus rendering
SCM accounting on the io_uring side unnecessary.

## References
- https://git.kernel.org/stable/c/18824f592aad4124d79751bbc1500ea86ac3ff29
- https://git.kernel.org/stable/c/3fe1ea5f921bf5b71cbfdc4469fb96c05936610e
- https://git.kernel.org/stable/c/5a33d385eb36991a91e3dddb189d8679e2aac2be
- https://git.kernel.org/stable/c/705318a99a138c29a512a72c3e0043b3cd7f55f4
- https://git.kernel.org/stable/c/bcedd497b3b4a0be56f3adf7c7542720eced0792
- https://git.kernel.org/stable/c/f2f57f51b53be153a522300454ddb3887722fb2c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52654.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-52654
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
