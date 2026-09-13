# [C] CVE-2017-8366

## Summary
Severity: Critical
Advisory: CVE-2017-8366
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-04-30
Source: https://osv.dev/vulnerability/CVE-2017-8366
Type: osv

## Details
The strescape function in ec_strings.c in Ettercap 0.8.2 allows remote attackers to cause a denial of service (heap-based buffer overflow and application crash) or possibly have unspecified other impact via a crafted filter that is mishandled by etterfilter.

## References
- http://www.debian.org/security/2017/dsa-3874
- https://blogs.gentoo.org/ago/2017/04/29/ettercap-etterfilter-heap-based-buffer-overflow-write/
