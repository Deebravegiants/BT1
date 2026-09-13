# [H] apparmor: fix unprivileged local user can do privileged policy management

## Summary
Severity: High
Advisory: CVE-2026-23268
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-03-18
Source: https://osv.dev/vulnerability/CVE-2026-23268
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.11.0 <5.10.253, >=5.11.0 <5.15.203, >=5.16.0 <6.1.169, >=6.2.0 <6.6.130, >=6.7.0 <6.12.77, >=6.13.0 <6.18.18, >=6.19.0 <6.19.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

apparmor: fix unprivileged local user can do privileged policy management

An unprivileged local user can load, replace, and remove profiles by
opening the apparmorfs interfaces, via a confused deputy attack, by
passing the opened fd to a privileged process, and getting the
privileged process to write to the interface.

This does require a privileged target that can be manipulated to do
the write for the unprivileged process, but once such access is
achieved full policy management is possible and all the possible
implications that implies: removing confinement, DoS of system or
target applications by denying all execution, by-passing the
unprivileged user namespace restriction, to exploiting kernel bugs for
a local privilege escalation.

The policy management interface can not have its permissions simply
changed from 0666 to 0600 because non-root processes need to be able
to load policy to different policy namespaces.

Instead ensure the task writing the interface has privileges that
are a subset of the task that opened the interface. This is already
done via policy for confined processes, but unconfined can delegate
access to the opened fd, by-passing the usual policy check.

## References
- https://git.kernel.org/stable/c/0fc63dd9170643d15c25681fca792539e23f4640
- https://git.kernel.org/stable/c/17debf5586020790b5717f96e5e6a3ca5bb961ab
- https://git.kernel.org/stable/c/33ee909702e047c94aaf41d4eea35626d509802c
- https://git.kernel.org/stable/c/4cafce4d6d0a66ec27e3af5637c11901d60189fa
- https://git.kernel.org/stable/c/6601e13e82841879406bf9f369032656f441a425
- https://git.kernel.org/stable/c/a407a078cd41b5261b99d822af784bd9f136eb4d
- https://git.kernel.org/stable/c/b60b3f7a35c46b2e0ca934f9c988b8fca06d76c6
- https://git.kernel.org/stable/c/b6a94eeca9c6c8f7c55ad44c62c98324f51ec596
- https://www.qualys.com/2026/03/10/crack-armor.txt
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/23xxx/CVE-2026-23268.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-23268
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
