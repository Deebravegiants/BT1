# [C] cifs: fix potential use-after-free bugs in TCP_Server_Info::hostname

## Summary
Severity: Critical
Advisory: CVE-2023-53751
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-08
Source: https://osv.dev/vulnerability/CVE-2023-53751
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.0.0 <6.1.28, >=6.2.0 <6.2.15, >=6.3.0 <6.3.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

cifs: fix potential use-after-free bugs in TCP_Server_Info::hostname

TCP_Server_Info::hostname may be updated once or many times during
reconnect, so protect its access outside reconnect path as well and
then prevent any potential use-after-free bugs.

## References
- https://git.kernel.org/stable/c/0b08c4c499200be67d54c439d56e5ea866869945
- https://git.kernel.org/stable/c/64d62ac6d6514cba1305bd08e271ec1843bdd612
- https://git.kernel.org/stable/c/90c49fce1c43e1cc152695e20363ff5087897c09
- https://git.kernel.org/stable/c/c511954bf142fe1995aec3c739a9f1a76990283a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53751.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53751
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
