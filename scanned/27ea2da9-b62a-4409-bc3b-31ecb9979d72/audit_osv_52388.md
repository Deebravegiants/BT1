# [M] CVE-2021-47396

## Summary
Severity: Medium
Advisory: CVE-2021-47396
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2021-47396
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

mac80211-hwsim: fix late beacon hrtimer handling

Thomas explained in https://lore.kernel.org/r/87mtoeb4hb.ffs@tglx
that our handling of the hrtimer here is wrong: If the timer fires
late (e.g. due to vCPU scheduling, as reported by Dmitry/syzbot)
then it tries to actually rearm the timer at the next deadline,
which might be in the past already:

 1          2          3          N          N+1
 |          |          |   ...    |          |

 ^ intended to fire here (1)
            ^ next deadline here (2)
                                      ^ actually fired here

The next time it fires, it's later, but will still try to schedule
for the next deadline (now 3), etc. until it catches up with N,
but that might take a long time, causing stalls etc.

Now, all of this is simulation, so we just have to fix it, but
note that the behaviour is wrong even per spec, since there's no
value then in sending all those beacons unaligned - they should be
aligned to the TBTT (1, 2, 3, ... in the picture), and if we're a
bit (or a lot) late, then just resume at that point.

Therefore, change the code to use hrtimer_forward_now() which will
ensure that the next firing of the timer would be at N+1 (in the
picture), i.e. the next interval point after the current time.

## References
- https://git.kernel.org/stable/c/2c204cf594df3b9468368dc9d0b24d482d93cda7
- https://git.kernel.org/stable/c/313bbd1990b6ddfdaa7da098d0c56b098a833572
- https://git.kernel.org/stable/c/9bee85de2c8155388c09a2e1530a243ec1c96f05
- https://git.kernel.org/stable/c/ed2adf69e29848d1eb9df99633dde655421c92ed
