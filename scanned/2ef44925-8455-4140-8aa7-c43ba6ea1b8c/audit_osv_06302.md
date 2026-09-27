# [M] BIT-libpython-2023-27043

## Summary
Severity: Medium
Advisory: BIT-libpython-2023-27043
Aliases: BIT-python-2023-27043, BIT-python-min-2023-27043, CVE-2023-27043, PSF-2023-2
Ecosystem: Bitnami
Published: 2025-08-11
Source: https://osv.dev/vulnerability/BIT-libpython-2023-27043
Type: osv

## Affected
- Bitnami: `libpython` — affected >=3.9.0 <3.9.20

## Details
The email module of Python through 3.11.3 incorrectly parses e-mail addresses that contain a special character. The wrong portion of an RFC2822 header is identified as the value of the addr-spec. In some applications, an attacker can bypass a protection mechanism in which application access is granted only after verifying receipt of e-mail to a specific domain (e.g., only @company.example.com addresses may be used for signup). This occurs in email/_parseaddr.py in recent versions of Python.

## References
- http://python.org
- https://github.com/python/cpython/issues/102988
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/4ZAEFSFZDNBNJPNOUTLG5COISGQDLMGV/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/75DTHSTNOFFNAWHXKMDXS7EJWC6W2FUC/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ARI7VDSNTQVXRQFM6IK5GSSLEIYV4VZH/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/BQAKLUJMHFGVBRDPEY57BJGNCE5UUPHW/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/HXYVPEZUA3465AEFX5JVFVP7KIFZMF3N/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/N6M5I6OQHJABNEYY555HUMMKX3Y4P25Z/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/NEUNZSZ3CVSM2QWVYH3N2XGOCDWNYUA3/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ORLXS5YTKN65E2Q2NWKXMFS5FWQHRNZW/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/P2MAICLFDDO3QVNHTZ2OCERZQ34R2PIC/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/P2W2BZQIHMCKRI5FNBJERFYMS5PK6TAH/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/PHVGRKQAGANCSGFI3QMYOCIMS4IFOZA5/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/PU6Y2S5CBN5BWCBDAJFTGIBZLK3S2G3J/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/QDRDDPDN3VFIYXJIYEABY6USX5EU66AG/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/RDDC2VOX7OQC6OHMYTVD4HLFZIV6PYBC/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/SINP4OVYNB2AGDYI2GS37EMW3H3F7XPZ/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/SOX7BCN6YL7B3RFPEEXPIU5CMTEHJOKR/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/VZXC32CJ7TWDPJO6GY2XIQRO7JZX5FLP/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/XWMBD4LNHWEXRI6YVFWJMTJQUL5WOFTS/
