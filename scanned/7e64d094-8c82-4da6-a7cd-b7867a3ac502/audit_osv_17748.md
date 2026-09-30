# [C] CVE-2020-1939

## Summary
Severity: Critical
Advisory: CVE-2020-1939
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-05-12
Source: https://osv.dev/vulnerability/CVE-2020-1939
Type: osv

## Details
The Apache NuttX (Incubating) project provides an optional separate "apps" repository which contains various optional components and example programs. One of these, ftpd, had a NULL pointer dereference bug. The NuttX RTOS itself is not affected. Users of the optional apps repository are affected only if they have enabled ftpd. Versions 6.15 to 8.2 are affected.

## References
- https://lists.apache.org/thread.html/re3adc65ff4d8d9c34e5bccba3941a28cbb0a47191c150df2727e101d%40%3Cdev.nuttx.apache.org%3E
