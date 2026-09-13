# [H] CVE-2018-0491

## Summary
Severity: High
Advisory: CVE-2018-0491
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-03-05
Source: https://osv.dev/vulnerability/CVE-2018-0491
Type: osv

## Details
A use-after-free issue was discovered in Tor 0.3.2.x before 0.3.2.10. It allows remote attackers to cause a denial of service (relay crash) because the KIST implementation allows a channel to be added more than once in the pending list.

## References
- https://blog.torproject.org/new-stable-tor-releases-security-fixes-and-dos-prevention-03210-03110-02915
- https://trac.torproject.org/projects/tor/ticket/24700
- https://trac.torproject.org/projects/tor/ticket/25117
- https://www.exploit-db.com/exploits/44994/
