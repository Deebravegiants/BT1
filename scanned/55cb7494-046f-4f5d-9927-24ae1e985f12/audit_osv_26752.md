# [C] cifs: fix session state check in reconnect to avoid use-after-free issue

## Summary
Severity: Critical
Advisory: CVE-2023-53794
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-09
Source: https://osv.dev/vulnerability/CVE-2023-53794
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.7.0 <6.1.47, >=6.2.0 <6.4.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

cifs: fix session state check in reconnect to avoid use-after-free issue

Don't collect exiting session in smb2_reconnect_server(), because it
will be released soon.

Note that the exiting session will stay in server->smb_ses_list until
it complete the cifs_free_ipc() and logoff() and then delete itself
from the list.

## References
- https://git.kernel.org/stable/c/759ffc164d95a32c09528766d74d9b4fb054e8f4
- https://git.kernel.org/stable/c/7e4f5c3f01fb0e51ca438e43262d858daf9a0a76
- https://git.kernel.org/stable/c/99f280700b4cc02d5f141b8d15f8e9fad0418f65
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53794.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53794
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
