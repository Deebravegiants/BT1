# [H] CVE-2017-10974

## Summary
Severity: High
Advisory: CVE-2017-10974
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2017-07-07
Source: https://osv.dev/vulnerability/CVE-2017-10974
Type: osv

## Details
Yaws 1.91 allows Unauthenticated Remote File Disclosure via HTTP Directory Traversal with /%5C../ to port 8080. NOTE: this CVE is only about use of an initial /%5C sequence to defeat traversal protection mechanisms; the initial /%5C sequence was apparently not discussed in earlier research on this product.

## References
- http://www.securityfocus.com/bid/99515
- http://hyp3rlinx.altervista.org/advisories/YAWS-WEB-SERVER-v1.91-UNAUTHENTICATED-REMOTE-FILE-DISCLOSURE.txt
- https://www.exploit-db.com/exploits/42303/
