# [H] HSI: ssi_protocol: Fix use after free vulnerability in ssi_protocol Driver Due to Race Condition

## Summary
Severity: High
Advisory: CVE-2025-37838
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-04-18
Source: https://osv.dev/vulnerability/CVE-2025-37838
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.8.0 <5.4.293, >=5.5.0 <5.10.237, >=5.11.0 <5.15.181, >=5.16.0 <6.1.135, >=6.2.0 <6.6.88, >=6.7.0 <6.12.24, >=6.13.0 <6.13.12, >=6.14.0 <6.14.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

HSI: ssi_protocol: Fix use after free vulnerability in ssi_protocol Driver Due to Race Condition

In the ssi_protocol_probe() function, &ssi->work is bound with
ssip_xmit_work(), In ssip_pn_setup(), the ssip_pn_xmit() function
within the ssip_pn_ops structure is capable of starting the
work.

If we remove the module which will call ssi_protocol_remove()
to make a cleanup, it will free ssi through kfree(ssi),
while the work mentioned above will be used. The sequence
of operations that may lead to a UAF bug is as follows:

CPU0                                    CPU1

                        | ssip_xmit_work
ssi_protocol_remove     |
kfree(ssi);             |
                        | struct hsi_client *cl = ssi->cl;
                        | // use ssi

Fix it by ensuring that the work is canceled before proceeding
with the cleanup in ssi_protocol_remove().

## References
- https://git.kernel.org/stable/c/4a8c29beb8a02b5a0a9d77d608aa14b6f88a6b86
- https://git.kernel.org/stable/c/4b4194c9a7a8f92db39e8e86c85f4fb12ebbec4f
- https://git.kernel.org/stable/c/58eb29dba712ab0f13af59ca2fe545f5ce360e78
- https://git.kernel.org/stable/c/72972552d0d0bfeb2dec5daf343a19018db36ffa
- https://git.kernel.org/stable/c/834e602d0cc7c743bfce734fad4a46cefc0f9ab1
- https://git.kernel.org/stable/c/ae5a6a0b425e8f76a9f0677e50796e494e89b088
- https://git.kernel.org/stable/c/d03abc1c2b21324550fa71e12d53e7d3498e0af6
- https://git.kernel.org/stable/c/d58493832e284f066e559b8da5ab20c15a2801d3
- https://git.kernel.org/stable/c/e3f88665a78045fe35c7669d2926b8d97b892c11
- https://lists.debian.org/debian-lts-announce/2025/05/msg00030.html
- https://lists.debian.org/debian-lts-announce/2025/05/msg00045.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/37xxx/CVE-2025-37838.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-37838
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
