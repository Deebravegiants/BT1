# [H] CVE-2018-0490

## Summary
Severity: High
Advisory: CVE-2018-0490
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-03-05
Source: https://osv.dev/vulnerability/CVE-2018-0490
Type: osv

## Details
An issue was discovered in Tor before 0.2.9.15, 0.3.1.x before 0.3.1.10, and 0.3.2.x before 0.3.2.10. The directory-authority protocol-list subprotocol implementation allows remote attackers to cause a denial of service (NULL pointer dereference and directory-authority crash) via a misformatted relay descriptor that is mishandled during voting.

## References
- https://blog.torproject.org/new-stable-tor-releases-security-fixes-and-dos-prevention-03210-03110-02915
- https://trac.torproject.org/projects/tor/ticket/25074
- https://www.debian.org/security/2018/dsa-4183
