# [M] CVE-2021-47252

## Summary
Severity: Medium
Advisory: CVE-2021-47252
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2021-47252
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

batman-adv: Avoid WARN_ON timing related checks

The soft/batadv interface for a queued OGM can be changed during the time
the OGM was queued for transmission and when the OGM is actually
transmitted by the worker.

But WARN_ON must be used to denote kernel bugs and not to print simple
warnings. A warning can simply be printed using pr_warn.

## References
- https://git.kernel.org/stable/c/e8e9d2968a9d08bf5c683afca182f1537edebf8d
- https://git.kernel.org/stable/c/282baa8104af44e04c4af3e7f933b44267c7f86f
- https://git.kernel.org/stable/c/2eb4e0b3631832a4291c8bf4c9db873f60b128c8
- https://git.kernel.org/stable/c/45011f2973f6b52cf50db397bb27bf805f5f0e7f
- https://git.kernel.org/stable/c/6031daaaf6d5c359c99dfffa102e332df234ff09
- https://git.kernel.org/stable/c/77a99aad5bc3ea105806ebae6be3cbadc2fc615e
- https://git.kernel.org/stable/c/9f460ae31c4435fd022c443a6029352217a16ac1
- https://git.kernel.org/stable/c/e7fbd8184fa9e85f0d648c499841cb7ff6dec9f4
