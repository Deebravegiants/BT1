# [H] rtnetlink: fix error logic of IFLA_BRIDGE_FLAGS writing back

## Summary
Severity: High
Advisory: CVE-2024-27414
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-17
Source: https://osv.dev/vulnerability/CVE-2024-27414
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.4.271, >=5.5.0 <5.10.212, >=5.11.0 <5.15.151, >=5.16.0 <6.1.81, >=6.2.0 <6.6.21, >=6.5.0 <6.7.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

rtnetlink: fix error logic of IFLA_BRIDGE_FLAGS writing back

In the commit d73ef2d69c0d ("rtnetlink: let rtnl_bridge_setlink checks
IFLA_BRIDGE_MODE length"), an adjustment was made to the old loop logic
in the function `rtnl_bridge_setlink` to enable the loop to also check
the length of the IFLA_BRIDGE_MODE attribute. However, this adjustment
removed the `break` statement and led to an error logic of the flags
writing back at the end of this function.

if (have_flags)
    memcpy(nla_data(attr), &flags, sizeof(flags));
    // attr should point to IFLA_BRIDGE_FLAGS NLA !!!

Before the mentioned commit, the `attr` is granted to be IFLA_BRIDGE_FLAGS.
However, this is not necessarily true fow now as the updated loop will let
the attr point to the last NLA, even an invalid NLA which could cause
overflow writes.

This patch introduces a new variable `br_flag` to save the NLA pointer
that points to IFLA_BRIDGE_FLAGS and uses it to resolve the mentioned
error logic.

## References
- https://git.kernel.org/stable/c/167d8642daa6a44b51de17f8ff0f584e1e762db7
- https://git.kernel.org/stable/c/743ad091fb46e622f1b690385bb15e3cd3daf874
- https://git.kernel.org/stable/c/831bc2728fb48a8957a824cba8c264b30dca1425
- https://git.kernel.org/stable/c/882a51a10ecf24ce135d573afa0872aef02c5125
- https://git.kernel.org/stable/c/a1227b27fcccc99dc44f912b479e01a17e2d7d31
- https://git.kernel.org/stable/c/b9fbc44159dfc3e9a7073032752d9e03f5194a6f
- https://git.kernel.org/stable/c/f2261eb994aa5757c1da046b78e3229a3ece0ad9
- https://lists.debian.org/debian-lts-announce/2024/06/msg00017.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/27xxx/CVE-2024-27414.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-27414
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
