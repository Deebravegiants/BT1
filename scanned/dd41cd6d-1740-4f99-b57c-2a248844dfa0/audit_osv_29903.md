# [C] smack: tcp: ipv4, fix incorrect labeling

## Summary
Severity: Critical
Advisory: CVE-2024-47659
Ecosystem: Linux
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2024-10-09
Source: https://osv.dev/vulnerability/CVE-2024-47659
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.30 <4.19.322, >=4.20.0 <5.4.284, >=5.5.0 <5.10.226, >=5.11.0 <5.15.167, >=5.16.0 <6.1.109, >=6.2.0 <6.6.50, >=6.7.0 <6.10.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

smack: tcp: ipv4, fix incorrect labeling

Currently, Smack mirrors the label of incoming tcp/ipv4 connections:
when a label 'foo' connects to a label 'bar' with tcp/ipv4,
'foo' always gets 'foo' in returned ipv4 packets. So,
1) returned packets are incorrectly labeled ('foo' instead of 'bar')
2) 'bar' can write to 'foo' without being authorized to write.

Here is a scenario how to see this:

* Take two machines, let's call them C and S,
   with active Smack in the default state
   (no settings, no rules, no labeled hosts, only builtin labels)

* At S, add Smack rule 'foo bar w'
   (labels 'foo' and 'bar' are instantiated at S at this moment)

* At S, at label 'bar', launch a program
   that listens for incoming tcp/ipv4 connections

* From C, at label 'foo', connect to the listener at S.
   (label 'foo' is instantiated at C at this moment)
   Connection succeedes and works.

* Send some data in both directions.
* Collect network traffic of this connection.

All packets in both directions are labeled with the CIPSO
of the label 'foo'. Hence, label 'bar' writes to 'foo' without
being authorized, and even without ever being known at C.

If anybody cares: exactly the same happens with DCCP.

This behavior 1st manifested in release 2.6.29.4 (see Fixes below)
and it looks unintentional. At least, no explanation was provided.

I changed returned packes label into the 'bar',
to bring it into line with the Smack documentation claims.

## References
- https://git.kernel.org/stable/c/0776bcf9cb6de46fdd94d10118de1cf9b05f83b9
- https://git.kernel.org/stable/c/0aea09e82eafa50a373fc8a4b84c1d4734751e2c
- https://git.kernel.org/stable/c/2fe209d0ad2e2729f7e22b9b31a86cc3ff0db550
- https://git.kernel.org/stable/c/4be9fd15c3c88775bdf6fa37acabe6de85beebff
- https://git.kernel.org/stable/c/5b4b304f196c070342e32a4752e1fa2e22fc0671
- https://git.kernel.org/stable/c/a948ec993541db4ef392b555c37a1186f4d61670
- https://git.kernel.org/stable/c/d3703fa94116fed91f64c7d1c7d284fb4369070f
- https://git.kernel.org/stable/c/d3f56c653c65f170b172d3c23120bc64ada645d8
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/47xxx/CVE-2024-47659.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-47659
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
