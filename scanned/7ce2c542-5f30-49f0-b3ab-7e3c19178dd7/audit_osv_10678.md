# [M] CVE-2017-18207

## Summary
Severity: Medium
Advisory: CVE-2017-18207
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-03-01
Source: https://osv.dev/vulnerability/CVE-2017-18207
Type: osv

## Details
The Wave_read._read_fmt_chunk function in Lib/wave.py in Python through 3.6.4 does not ensure a nonzero channel value, which allows attackers to cause a denial of service (divide-by-zero and exception) via a crafted wav format audio file. NOTE: the vendor disputes this issue because Python applications "need to be prepared to handle a wide variety of exceptions.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-01/msg00040.html
- https://bugs.python.org/issue32056
