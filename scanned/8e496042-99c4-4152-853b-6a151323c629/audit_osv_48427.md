# [H] CVE-2017-7618

## Summary
Severity: High
Advisory: CVE-2017-7618
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-04-10
Source: https://osv.dev/vulnerability/CVE-2017-7618
Type: osv

## Details
crypto/ahash.c in the Linux kernel through 4.10.9 allows attackers to cause a denial of service (API operation calling its own callback, and infinite recursion) by triggering EBUSY on a full queue.

## References
- https://support.hpe.com/hpsc/doc/public/display?docLocale=en_US&docId=emr_na-hpesbhf03800en_us
- http://marc.info/?l=linux-crypto-vger&m=149181655623850&w=2
- http://www.securityfocus.com/bid/97534
