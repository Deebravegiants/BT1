# [M] CVE-2020-24385

## Summary
Severity: Medium
Advisory: CVE-2020-24385
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-09-03
Source: https://osv.dev/vulnerability/CVE-2020-24385
Type: osv

## Details
In MidnightBSD before 1.2.6 and 1.3 before August 2020, and FreeBSD before 7, a NULL pointer dereference was found in the Linux emulation layer that allows attackers to crash the running kernel. During binary interaction, td->td_emuldata in sys/compat/linux/linux_emul.h is not getting initialized and returns NULL from em_find().

## References
- http://www.midnightbsd.org/security/adv/MIDNIGHTBSD-SA-20:02.txt
- https://www.midnightbsd.org/notes/
