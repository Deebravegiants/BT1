# [H] CVE-2016-6831

## Summary
Severity: High
Advisory: CVE-2016-6831
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-01-10
Source: https://osv.dev/vulnerability/CVE-2016-6831
Type: osv

## Details
The "process-execute" and "process-spawn" procedures did not free memory correctly when the execve() call failed, resulting in a memory leak. This could be abused by an attacker to cause resource exhaustion or a denial of service. This affects all releases of CHICKEN up to and including 4.11 (it will be fixed in 4.12 and 5.0, which are not yet released).

## References
- http://www.securityfocus.com/bid/92550
- http://lists.nongnu.org/archive/html/chicken-announce/2016-08/msg00001.html
