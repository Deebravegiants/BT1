# [C] CVE-2016-8339

## Summary
Severity: Critical
Advisory: CVE-2016-8339
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-10-28
Source: https://osv.dev/vulnerability/CVE-2016-8339
Type: osv

## Details
A buffer overflow in Redis 3.2.x prior to 3.2.4 causes arbitrary code execution when a crafted command is sent. An out of bounds write vulnerability exists in the handling of the client-output-buffer-limit option during the CONFIG SET command for the Redis data structure store. A crafted CONFIG SET command can lead to an out of bounds write potentially resulting in code execution.

## References
- http://www.securityfocus.com/bid/93283
- https://security.gentoo.org/glsa/201702-16
- https://github.com/antirez/redis/commit/6d9f8e2462fc2c426d48c941edeb78e5df7d2977
- http://www.talosintelligence.com/reports/TALOS-2016-0206/
