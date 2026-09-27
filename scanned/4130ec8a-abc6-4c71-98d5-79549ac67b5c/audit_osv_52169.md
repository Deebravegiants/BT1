# [H] CVE-2021-47153

## Summary
Severity: High
Advisory: CVE-2021-47153
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2024-03-25
Source: https://osv.dev/vulnerability/CVE-2021-47153
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

i2c: i801: Don't generate an interrupt on bus reset

Now that the i2c-i801 driver supports interrupts, setting the KILL bit
in a attempt to recover from a timed out transaction triggers an
interrupt. Unfortunately, the interrupt handler (i801_isr) is not
prepared for this situation and will try to process the interrupt as
if it was signaling the end of a successful transaction. In the case
of a block transaction, this can result in an out-of-range memory
access.

This condition was reproduced several times by syzbot:
https://syzkaller.appspot.com/bug?extid=ed71512d469895b5b34e
https://syzkaller.appspot.com/bug?extid=8c8dedc0ba9e03f6c79e
https://syzkaller.appspot.com/bug?extid=c8ff0b6d6c73d81b610e
https://syzkaller.appspot.com/bug?extid=33f6c360821c399d69eb
https://syzkaller.appspot.com/bug?extid=be15dc0b1933f04b043a
https://syzkaller.appspot.com/bug?extid=b4d3fd1dfd53e90afd79

So disable interrupts while trying to reset the bus. Interrupts will
be enabled again for the following transaction.

## References
- https://git.kernel.org/stable/c/1f583d3813f204449037cd2acbfc09168171362a
- https://git.kernel.org/stable/c/b523feb7e8e44652f92f3babb953a976e7ccbbef
- https://git.kernel.org/stable/c/c70e1ba2e7e65255a0ce004f531dd90dada97a8c
- https://git.kernel.org/stable/c/dfa8929e117b0228a7765f5c3f5988a4a028f3c6
- https://git.kernel.org/stable/c/e4d8716c3dcec47f1557024add24e1f3c09eb24b
- https://git.kernel.org/stable/c/f9469082126cebb7337db3992d143f5e4edfe629
- https://git.kernel.org/stable/c/04cc05e3716ae31b17ecdab7bc55c8170def1b8b
- https://git.kernel.org/stable/c/09c9e79f4c10cfb6b9e0e1b4dd355232e4b5a3b3
