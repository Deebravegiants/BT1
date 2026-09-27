# [H] BIT-libpython-2023-24329

## Summary
Severity: High
Advisory: BIT-libpython-2023-24329
Aliases: BIT-python-2023-24329, BIT-python-min-2023-24329, CVE-2023-24329, PSF-2023-1
Ecosystem: Bitnami
Published: 2025-08-11
Source: https://osv.dev/vulnerability/BIT-libpython-2023-24329
Type: osv

## Affected
- Bitnami: `libpython` — affected >=3.11.0 <3.11.4

## Details
An issue in the urllib.parse component of Python before 3.11.4 allows attackers to bypass blocklisting methods by supplying a URL that starts with blank characters.

## References
- https://github.com/python/cpython/issues/102153
- https://github.com/python/cpython/pull/99421
- https://lists.debian.org/debian-lts-announce/2023/09/msg00022.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/6PEVICI7YNGGMSL3UCMWGE66QFLATH72/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/DSL6NSOAXWBJJ67XPLSSC74MNKZF3BBO/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/EM2XLZSTXG44TMFXF4E6VTGKR2MQCW3G/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/F2NY75GFDZ5T6YPN44D3VMFT5SUVTOTG/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/GR5US3BYILYJ4SKBV6YBNPRUBAL5P2CN/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/H23OSKC6UG6IWOQAUPW74YUHWRWVXJP7/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/JZTLGV2HYFF4AMYJL25VDIGAIHCU7UPA/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/LWC4WGXER5P6Q75RFGL7QUTPP3N5JR7T/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/MZEHSXSCMA4WWQKXT6QV7AAR6SWNZ2VP/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/O5SP4RT3RRS434ZS2HQKQJ3VZW7YPKYR/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/OHHJHJRLEF3TDT2K3676CAUVRDD4CCMR/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/PEUN6T22UJFXR7J5F6UUHCXXPKJ2DVHI/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/PURM5CFDABEWAIWZFD2MQ7ZJGCPYSQ44/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/Q3J5N24ECS4B6MJDRO6UAYU6GPLYBDCL/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/QRQHN7RWJQJHYP6E5EKESOYP5VDSHZG4/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/RA2MBEEES6L46OD64OBSVUUMGKNGMOWW/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/T4IDB5OAR5Y4UK3HLMZBW4WEL2B7YFMJ/
