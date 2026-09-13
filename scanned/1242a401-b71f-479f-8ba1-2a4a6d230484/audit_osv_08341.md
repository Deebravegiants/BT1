# [C] CVE-2016-2337

## Summary
Severity: Critical
Advisory: CVE-2016-2337
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-01-06
Source: https://osv.dev/vulnerability/CVE-2016-2337
Type: osv

## Details
Type confusion exists in _cancel_eval Ruby's TclTkIp class method. Attacker passing different type of object than String as "retval" argument can cause arbitrary code execution.

## References
- http://www.securityfocus.com/bid/91233
- https://lists.debian.org/debian-lts-announce/2018/08/msg00028.html
- https://security.gentoo.org/glsa/201710-18
- http://www.talosintelligence.com/reports/TALOS-2016-0031/
