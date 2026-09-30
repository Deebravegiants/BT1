# [C] sunrpc: fix handling of server side tls alerts

## Summary
Severity: Critical
Advisory: CVE-2025-38566
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-08-19
Source: https://osv.dev/vulnerability/CVE-2025-38566
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.4.0 <6.6.102, >=6.7.0 <6.12.42, >=6.13.0 <6.15.10, >=6.16.0 <6.16.1

## Details
In the Linux kernel, the following vulnerability has been resolved:

sunrpc: fix handling of server side tls alerts

Scott Mayhew discovered a security exploit in NFS over TLS in
tls_alert_recv() due to its assumption it can read data from
the msg iterator's kvec..

kTLS implementation splits TLS non-data record payload between
the control message buffer (which includes the type such as TLS
aler or TLS cipher change) and the rest of the payload (say TLS
alert's level/description) which goes into the msg payload buffer.

This patch proposes to rework how control messages are setup and
used by sock_recvmsg().

If no control message structure is setup, kTLS layer will read and
process TLS data record types. As soon as it encounters a TLS control
message, it would return an error. At that point, NFS can setup a
kvec backed msg buffer and read in the control message such as a
TLS alert. Msg iterator can advance the kvec pointer as a part of
the copy process thus we need to revert the iterator before calling
into the tls_alert_recv.

## References
- https://git.kernel.org/stable/c/25bb3647d30a20486b5fe7cff2b0e503c16c9692
- https://git.kernel.org/stable/c/3b549da875414989f480b66835d514be80a0bd9c
- https://git.kernel.org/stable/c/6b33c31cc788073bfbed9297e1f4486ed73d87da
- https://git.kernel.org/stable/c/b1df394621710b312f0393e3f240fdac0764f968
- https://git.kernel.org/stable/c/bee47cb026e762841f3faece47b51f985e215edb
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38566.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38566
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
