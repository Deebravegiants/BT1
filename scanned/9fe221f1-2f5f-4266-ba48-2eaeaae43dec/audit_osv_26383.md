# [C] cifs: Fix oops due to uncleared server->smbd_conn in reconnect

## Summary
Severity: Critical
Advisory: CVE-2023-53006
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-03-27
Source: https://osv.dev/vulnerability/CVE-2023-53006
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.16.0 <4.19.272, >=4.20.0 <5.4.231, >=5.5.0 <5.10.166, >=5.11.0 <5.15.91, >=5.16.0 <6.1.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

cifs: Fix oops due to uncleared server->smbd_conn in reconnect

In smbd_destroy(), clear the server->smbd_conn pointer after freeing the
smbd_connection struct that it points to so that reconnection doesn't get
confused.

## References
- https://git.kernel.org/stable/c/4b83bc6f87eedab4599b0123e572a422689444be
- https://git.kernel.org/stable/c/5109607a4ece7cd8536172bf7549eb4dce1f3576
- https://git.kernel.org/stable/c/91be54849d5392050f5b847b42bd5e6221551ac8
- https://git.kernel.org/stable/c/a9640c0b268405f2540e8203a545e930ea88bb7d
- https://git.kernel.org/stable/c/b7ab9161cf5ddc42a288edf9d1a61f3bdffe17c7
- https://git.kernel.org/stable/c/e037baee16e0b9ace7e730888fcae9cec11daff2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53006.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53006
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
