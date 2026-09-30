# [H] nvme-tcp: fix NULL pointer dereferences in nvmet_tcp_build_pdu_iovec

## Summary
Severity: High
Advisory: CVE-2026-22998
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-01-25
Source: https://osv.dev/vulnerability/CVE-2026-22998
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.10.249, >=5.11.0 <5.15.199, >=5.16.0 <6.1.162, >=6.2.0 <6.6.122, >=6.7.0 <6.12.67, >=6.8.0 <6.18.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

nvme-tcp: fix NULL pointer dereferences in nvmet_tcp_build_pdu_iovec

Commit efa56305908b ("nvmet-tcp: Fix a kernel panic when host sends an invalid H2C PDU length")
added ttag bounds checking and data_offset
validation in nvmet_tcp_handle_h2c_data_pdu(), but it did not validate
whether the command's data structures (cmd->req.sg and cmd->iov) have
been properly initialized before processing H2C_DATA PDUs.

The nvmet_tcp_build_pdu_iovec() function dereferences these pointers
without NULL checks. This can be triggered by sending H2C_DATA PDU
immediately after the ICREQ/ICRESP handshake, before
sending a CONNECT command or NVMe write command.

Attack vectors that trigger NULL pointer dereferences:
1. H2C_DATA PDU sent before CONNECT → both pointers NULL
2. H2C_DATA PDU for READ command → cmd->req.sg allocated, cmd->iov NULL
3. H2C_DATA PDU for uninitialized command slot → both pointers NULL

The fix validates both cmd->req.sg and cmd->iov before calling
nvmet_tcp_build_pdu_iovec(). Both checks are required because:
- Uninitialized commands: both NULL
- READ commands: cmd->req.sg allocated, cmd->iov NULL
- WRITE commands: both allocated

## References
- https://git.kernel.org/stable/c/32b63acd78f577b332d976aa06b56e70d054cbba
- https://git.kernel.org/stable/c/374b095e265fa27465f34780e0eb162ff1bef913
- https://git.kernel.org/stable/c/3def5243150716be86599c2a1767c29c68838b6d
- https://git.kernel.org/stable/c/76abc83a9d25593c2b7613c549413079c14a4686
- https://git.kernel.org/stable/c/7d75570002929d20e40110d6b03e46202c9d1bc7
- https://git.kernel.org/stable/c/baabe43a0edefac8cd7b981ff87f967f6034dafe
- https://git.kernel.org/stable/c/fdecd3b6aac10d5a18d0dc500fe57f8648b66cd4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/22xxx/CVE-2026-22998.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-22998
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
