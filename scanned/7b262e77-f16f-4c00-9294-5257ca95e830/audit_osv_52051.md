# [H] CVE-2021-47010

## Summary
Severity: High
Advisory: CVE-2021-47010
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-02-28
Source: https://osv.dev/vulnerability/CVE-2021-47010
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: Only allow init netns to set default tcp cong to a restricted algo

tcp_set_default_congestion_control() is netns-safe in that it writes
to &net->ipv4.tcp_congestion_control, but it also sets
ca->flags |= TCP_CONG_NON_RESTRICTED which is not namespaced.
This has the unintended side-effect of changing the global
net.ipv4.tcp_allowed_congestion_control sysctl, despite the fact that it
is read-only: 97684f0970f6 ("net: Make tcp_allowed_congestion_control
readonly in non-init netns")

Resolve this netns "leak" by only allowing the init netns to set the
default algorithm to one that is restricted. This restriction could be
removed if tcp_allowed_congestion_control were namespace-ified in the
future.

This bug was uncovered with
https://github.com/JonathonReinhart/linux-netns-sysctl-verify

## References
- https://git.kernel.org/stable/c/efe1532a6e1a8e3c343d04fff510f0ed80328f9c
- https://git.kernel.org/stable/c/6c1ea8bee75df8fe2184a50fcd0f70bf82986f42
- https://git.kernel.org/stable/c/8d432592f30fcc34ef5a10aac4887b4897884493
- https://git.kernel.org/stable/c/9884f745108f7d25b189bbcd6754e284fb29ab68
- https://git.kernel.org/stable/c/992de06308d9a9584d59b96d294ac676f924e437
- https://git.kernel.org/stable/c/e7d7bedd507bb732e600403b7a96f9fe48d0ca31
