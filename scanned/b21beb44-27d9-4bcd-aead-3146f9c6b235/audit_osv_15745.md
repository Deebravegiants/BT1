# [C] CVE-2019-19330

## Summary
Severity: Critical
Advisory: CVE-2019-19330
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-11-27
Source: https://osv.dev/vulnerability/CVE-2019-19330
Type: osv

## Details
The HTTP/2 implementation in HAProxy before 2.0.10 mishandles headers, as demonstrated by carriage return (CR, ASCII 0xd), line feed (LF, ASCII 0xa), and the zero character (NUL, ASCII 0x0), aka Intermediary Encapsulation Attacks.

## References
- https://git.haproxy.org/?p=haproxy.git%3Ba=commit%3Bh=146f53ae7e97dbfe496d0445c2802dd0a30b0878
- https://git.haproxy.org/?p=haproxy.git%3Ba=commit%3Bh=54f53ef7ce4102be596130b44c768d1818570344
- https://git.haproxy.org/?p=haproxy-2.0.git%3Ba=commit%3Bh=ac198b92d461515551b95daae20954b3053ce87e
- https://seclists.org/bugtraq/2019/Nov/45
- https://security.gentoo.org/glsa/202004-01
- https://tools.ietf.org/html/rfc7540#section-10.3
- https://usn.ubuntu.com/4212-1/
- https://www.debian.org/security/2019/dsa-4577
