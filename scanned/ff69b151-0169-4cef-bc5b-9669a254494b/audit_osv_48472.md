# [C] CVE-2017-7938

## Summary
Severity: Critical
Advisory: CVE-2017-7938
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-04-20
Source: https://osv.dev/vulnerability/CVE-2017-7938
Type: osv

## Details
Stack-based buffer overflow in DMitry (Deepmagic Information Gathering Tool) version 1.3a (Unix) allows attackers to cause a denial of service (application crash) or possibly have unspecified other impact via a long argument. An example threat model is automated execution of DMitry with hostname strings found in local log files.

## References
- https://www.exploit-db.com/exploits/41898/
- https://lists.debian.org/debian-lts-announce/2024/10/msg00024.html
- https://github.com/jaygreig86/dmitry/pull/12
- https://cxsecurity.com/issue/WLB-2017040113
- https://packetstormsecurity.com/files/142210/Dmitry-1.3a-Local-Stack-Buffer-Overflow.html
