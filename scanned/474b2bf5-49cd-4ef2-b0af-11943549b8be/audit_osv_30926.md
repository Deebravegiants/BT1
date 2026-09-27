# [M] rtc: check if __rtc_read_time was successful in rtc_timer_do_work()

## Summary
Severity: Medium
Advisory: CVE-2024-56739
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-12-29
Source: https://osv.dev/vulnerability/CVE-2024-56739
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.38 <4.19.325, >=4.20.0 <5.4.287, >=5.5.0 <5.10.231, >=5.11.0 <5.15.174, >=5.16.0 <6.1.120, >=6.2.0 <6.6.64, >=6.7.0 <6.11.11, >=6.12.0 <6.12.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

rtc: check if __rtc_read_time was successful in rtc_timer_do_work()

If the __rtc_read_time call fails,, the struct rtc_time tm; may contain
uninitialized data, or an illegal date/time read from the RTC hardware.

When calling rtc_tm_to_ktime later, the result may be a very large value
(possibly KTIME_MAX). If there are periodic timers in rtc->timerqueue,
they will continually expire, may causing kernel softlockup.

## References
- https://git.kernel.org/stable/c/0d68e8514d9040108ff7d1b37ca71096674b6efe
- https://git.kernel.org/stable/c/246f621d363988e7040f4546d20203dc713fa3e1
- https://git.kernel.org/stable/c/39ad0a1ae17b54509cd9e93dcd8cec16e7c12d3f
- https://git.kernel.org/stable/c/44b3257ff705d63d5f00ef8ed314a0eeb7ec37f2
- https://git.kernel.org/stable/c/a1f0b4af90cc18b10261ecde56c6a56b22c75bd1
- https://git.kernel.org/stable/c/dd4b1cbcc916fad5d10c2662b62def9f05e453d4
- https://git.kernel.org/stable/c/e77bce0a8c3989b4173c36f4195122bca8f4a3e1
- https://git.kernel.org/stable/c/e8ba8a2bc4f60a1065f23d6a0e7cbea945a0f40d
- https://git.kernel.org/stable/c/fde56535505dde3336df438e949ef4742b6d6d6e
- https://lists.debian.org/debian-lts-announce/2025/03/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/56xxx/CVE-2024-56739.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-56739
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
