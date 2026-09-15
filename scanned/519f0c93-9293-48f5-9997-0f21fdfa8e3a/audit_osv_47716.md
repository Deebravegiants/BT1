# [M] CVE-2017-10792

## Summary
Severity: Medium
Advisory: CVE-2017-10792
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-07-02
Source: https://osv.dev/vulnerability/CVE-2017-10792
Type: osv

## Details
There is a NULL Pointer Dereference in the function ll_insert() of the libpspp library in GNU PSPP before 0.11.0. For example, a crash was observed within the library code when attempting to convert invalid SPSS data into CSV format. A crafted input will lead to a remote denial of service attack.

## References
- http://lists.gnu.org/archive/html/pspp-announce/2017-08/msg00000.html
- http://www.securityfocus.com/bid/99385
- https://bugzilla.redhat.com/show_bug.cgi?id=1467005
