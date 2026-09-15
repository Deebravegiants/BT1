# [H] net/sched: act_mirred: don't override retval if we already lost the skb

## Summary
Severity: High
Advisory: CVE-2024-26739
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-04-03
Source: https://osv.dev/vulnerability/CVE-2024-26739
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.19.0 <5.10.238, >=5.11.0 <5.15.182, >=5.16.0 <6.1.136, >=6.2.0 <6.6.19, >=6.7.0 <6.7.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

net/sched: act_mirred: don't override retval if we already lost the skb

If we're redirecting the skb, and haven't called tcf_mirred_forward(),
yet, we need to tell the core to drop the skb by setting the retcode
to SHOT. If we have called tcf_mirred_forward(), however, the skb
is out of our hands and returning SHOT will lead to UaF.

Move the retval override to the error path which actually need it.

## References
- https://git.kernel.org/stable/c/0117fe0a4615a7c8d30d6ebcbf87332fbe63e6fd
- https://git.kernel.org/stable/c/166c2c8a6a4dc2e4ceba9e10cfe81c3e469e3210
- https://git.kernel.org/stable/c/28cdbbd38a4413b8eff53399b3f872fd4e80db9d
- https://git.kernel.org/stable/c/9d3ef89b6a5e9f2e940de2cef3d543be0be8dec5
- https://git.kernel.org/stable/c/e873e8f7d03a2ee5b77fb1a305c782fed98e2754
- https://git.kernel.org/stable/c/f4e294bbdca8ac8757db436fc82214f3882fc7e7
- https://lists.debian.org/debian-lts-announce/2025/05/msg00045.html
- https://lists.debian.org/debian-lts-announce/2025/10/msg00007.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/26xxx/CVE-2024-26739.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-26739
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
