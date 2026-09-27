# [M] CVE-2017-11189

## Summary
Severity: Medium
Advisory: CVE-2017-11189
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-07-12
Source: https://osv.dev/vulnerability/CVE-2017-11189
Type: osv

## Details
unrarlib.c in unrar-free 0.0.1 might allow remote attackers to cause a denial of service (NULL pointer dereference and application crash), which could be relevant if unrarlib is used as library code for a long-running application. NOTE: one of the several test cases in the references may be the same as what was separately reported as CVE-2017-14121.

## References
- https://github.com/0x09AL/my-exploits/tree/master/pocs/unrar-free/dos
