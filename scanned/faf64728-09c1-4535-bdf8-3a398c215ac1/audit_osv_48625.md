# [H] CVE-2018-10115

## Summary
Severity: High
Advisory: CVE-2018-10115
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-05-02
Source: https://osv.dev/vulnerability/CVE-2018-10115
Type: osv

## Details
Incorrect initialization logic of RAR decoder objects in 7-Zip 18.03 and before can lead to usage of uninitialized memory, allowing remote attackers to cause a denial of service (segmentation fault) or execute arbitrary code via a crafted RAR archive.

## References
- http://www.securityfocus.com/bid/104132
- http://www.securitytracker.com/id/1040832
- https://sourceforge.net/p/sevenzip/discussion/45797/thread/adc65bfa/
- https://landave.io/2018/05/7-zip-from-uninitialized-memory-to-remote-code-execution/
