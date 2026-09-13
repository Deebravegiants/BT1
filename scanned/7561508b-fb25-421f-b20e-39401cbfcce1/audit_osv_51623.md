# [C] CVE-2021-36159

## Summary
Severity: Critical
Advisory: CVE-2021-36159
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2021-08-03
Source: https://osv.dev/vulnerability/CVE-2021-36159
Type: osv

## Details
libfetch before 2021-07-26, as used in apk-tools, xbps, and other products, mishandles numeric strings for the FTP and HTTP protocols. The FTP passive mode implementation allows an out-of-bounds read because strtol is used to parse the relevant numbers into address bytes. It does not check if the line ends prematurely. If it does, the for-loop condition checks for the '\0' terminator one byte too late.

## References
- https://lists.apache.org/thread.html/r61db8e7dcb56dc000a5387a88f7a473bacec5ee01b9ff3f55308aacc%40%3Cdev.kafka.apache.org%3E
- https://lists.apache.org/thread.html/r61db8e7dcb56dc000a5387a88f7a473bacec5ee01b9ff3f55308aacc%40%3Cusers.kafka.apache.org%3E
- https://lists.apache.org/thread.html/rbf4ce74b0d1fa9810dec50ba3ace0caeea677af7c27a97111c06ccb7%40%3Cdev.kafka.apache.org%3E
- https://lists.apache.org/thread.html/rbf4ce74b0d1fa9810dec50ba3ace0caeea677af7c27a97111c06ccb7%40%3Cusers.kafka.apache.org%3E
- https://github.com/freebsd/freebsd-src/commits/main/lib/libfetch
- https://gitlab.alpinelinux.org/alpine/apk-tools/-/issues/10749
