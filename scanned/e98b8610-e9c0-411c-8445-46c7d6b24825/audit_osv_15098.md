# [H] CVE-2019-13351

## Summary
Severity: High
Advisory: CVE-2019-13351
CVSS: 8.1 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-07-05
Source: https://osv.dev/vulnerability/CVE-2019-13351
Type: osv

## Details
posix/JackSocket.cpp in libjack in JACK2 1.9.1 through 1.9.12 (as distributed with alsa-plugins 1.1.7 and later) has a "double file descriptor close" issue during a failed connection attempt when jackd2 is not running. Exploitation success depends on multithreaded timing of that double close, which can result in unintended information disclosure, crashes, or file corruption due to having the wrong file associated with the file descriptor.

## References
- https://github.com/jackaudio/jack2/pull/480
- https://github.com/xbmc/xbmc/issues/16258
