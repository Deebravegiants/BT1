# [H] net/smc: avoid data corruption caused by decline

## Summary
Severity: High
Advisory: CVE-2023-52775
Ecosystem: Linux
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:L)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2023-52775
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.8.0 <5.10.203, >=5.11.0 <5.15.141, >=5.16.0 <6.1.65, >=6.2.0 <6.6.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

net/smc: avoid data corruption caused by decline

We found a data corruption issue during testing of SMC-R on Redis
applications.

The benchmark has a low probability of reporting a strange error as
shown below.

"Error: Protocol error, got "\xe2" as reply type byte"

Finally, we found that the retrieved error data was as follows:

0xE2 0xD4 0xC3 0xD9 0x04 0x00 0x2C 0x20 0xA6 0x56 0x00 0x16 0x3E 0x0C
0xCB 0x04 0x02 0x01 0x00 0x00 0x20 0x00 0x00 0x00 0x00 0x00 0x00 0x00
0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0xE2

It is quite obvious that this is a SMC DECLINE message, which means that
the applications received SMC protocol message.
We found that this was caused by the following situations:

client                  server
        ¦  clc proposal
        ------------->
        ¦  clc accept
        <-------------
        ¦  clc confirm
        ------------->
wait llc confirm
			send llc confirm
        ¦failed llc confirm
        ¦   x------
(after 2s)timeout
                        wait llc confirm rsp

wait decline

(after 1s) timeout
                        (after 2s) timeout
        ¦   decline
        -------------->
        ¦   decline
        <--------------

As a result, a decline message was sent in the implementation, and this
message was read from TCP by the already-fallback connection.

This patch double the client timeout as 2x of the server value,
With this simple change, the Decline messages should never cross or
collide (during Confirm link timeout).

This issue requires an immediate solution, since the protocol updates
involve a more long-term solution.

## References
- https://git.kernel.org/stable/c/5ada292b5c504720a0acef8cae9acc62a694d19c
- https://git.kernel.org/stable/c/7234d2b5dffa5af77fd4e0deaebab509e130c6b1
- https://git.kernel.org/stable/c/90072af9efe8c7bd7d086709014ddd44cebd5e7c
- https://git.kernel.org/stable/c/94a0ae698b4d5d5bb598e23228002a1491c50add
- https://git.kernel.org/stable/c/e6d71b437abc2f249e3b6a1ae1a7228e09c6e563
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52775.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-52775
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
