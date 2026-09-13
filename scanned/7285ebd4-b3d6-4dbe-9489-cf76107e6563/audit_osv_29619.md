# [H] net: hns3: fix a deadlock problem when config TC during resetting

## Summary
Severity: High
Advisory: CVE-2024-44995
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-09-04
Source: https://osv.dev/vulnerability/CVE-2024-44995
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.15.0 <5.4.283, >=5.5.0 <5.10.225, >=5.11.0 <5.15.166, >=5.16.0 <6.1.107, >=6.2.0 <6.6.48, >=6.7.0 <6.10.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: hns3: fix a deadlock problem when config TC during resetting

When config TC during the reset process, may cause a deadlock, the flow is
as below:
                             pf reset start
                                 │
                                 ▼
                              ......
setup tc                         │
    │                            ▼
    ▼                      DOWN: napi_disable()
napi_disable()(skip)             │
    │                            │
    ▼                            ▼
  ......                      ......
    │                            │
    ▼                            │
napi_enable()                    │
                                 ▼
                           UINIT: netif_napi_del()
                                 │
                                 ▼
                              ......
                                 │
                                 ▼
                           INIT: netif_napi_add()
                                 │
                                 ▼
                              ......                 global reset start
                                 │                      │
                                 ▼                      ▼
                           UP: napi_enable()(skip)    ......
                                 │                      │
                                 ▼                      ▼
                              ......                 napi_disable()

In reset process, the driver will DOWN the port and then UINIT, in this
case, the setup tc process will UP the port before UINIT, so cause the
problem. Adds a DOWN process in UINIT to fix it.

## References
- https://git.kernel.org/stable/c/195918217448a6bb7f929d6a2ffffce9f1ece1cc
- https://git.kernel.org/stable/c/67492d4d105c0a6321b00c393eec96b9a7a97a16
- https://git.kernel.org/stable/c/6ae2b7d63cd056f363045eb65409143e16f23ae8
- https://git.kernel.org/stable/c/be5e816d00a506719e9dbb1a9c861c5ced30a109
- https://git.kernel.org/stable/c/de37408d5c26fc4a296a28a0c96dcb814219bfa1
- https://git.kernel.org/stable/c/fa1d4de7265c370e673583ac8d1bd17d21826cd9
- https://git.kernel.org/stable/c/fc250eca15bde34c4c8f806b9d88f55bd56a992c
- https://lists.debian.org/debian-lts-announce/2024/10/msg00003.html
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/44xxx/CVE-2024-44995.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-44995
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
