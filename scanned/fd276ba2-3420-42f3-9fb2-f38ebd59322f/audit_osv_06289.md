# [C] BIT-libpython-2021-3177

## Summary
Severity: Critical
Advisory: BIT-libpython-2021-3177
Aliases: BIT-python-2021-3177, BIT-python-min-2021-3177, CVE-2021-3177, PSF-2021-3
Ecosystem: Bitnami
Published: 2025-08-11
Source: https://osv.dev/vulnerability/BIT-libpython-2021-3177
Type: osv

## Affected
- Bitnami: `libpython` — affected >=3.9.0 <3.9.2

## Details
Python 3.x through 3.9.1 has a buffer overflow in PyCArg_repr in _ctypes/callproc.c, which may lead to remote code execution in certain Python applications that accept floating-point numbers as untrusted input, as demonstrated by a 1e300 argument to c_double.from_param. This occurs because sprintf is used unsafely.

## References
- https://bugs.python.org/issue42938
- https://github.com/python/cpython/pull/24239
- https://lists.apache.org/thread.html/rf9fa47ab66495c78bb4120b0754dd9531ca2ff0430f6685ac9b07772%40%3Cdev.mina.apache.org%3E
- https://lists.debian.org/debian-lts-announce/2021/04/msg00005.html
- https://lists.debian.org/debian-lts-announce/2022/02/msg00013.html
- https://lists.debian.org/debian-lts-announce/2023/05/msg00024.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/BRHOCQYX3QLDGDQGTWQAUUT2GGIZCZUO/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/CCFZMVRQUKCBQIG5F2CBVADK63NFSE4A/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/FONHJIOZOFD7CD35KZL6SVBUTMBPGZGA/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/FPE7SMXYUIWPOIZV4DQYXODRXMFX3C5E/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/HCQTCSP6SCVIYNIRUJC5X7YBVUHPLSC4/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/MGSV6BJQLRQ6RKVUXK7JGU7TP4QFGQXC/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/MP572OLHMS7MZO4KUPSCIMSZIA5IZZ62/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/NODWHDIFBQE5RU5PUWUVE47JOT5VCMJ2/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/NQPARTLNSFQVMMQHPNBFOCOZOO3TMQNA/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/NXSMBHES3ANXXS2RSO5G6Q24BR4B2PWK/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/V6XJAULOS5JVB2L67NCKKMJ5NTKZJBSD/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/Y4KSYYWMGAKOA2JVCQA422OINT6CKQ7O/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/YDTZVGSXQ7HR7OCGSUHTRNTMBG43OMKU/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/Z7GZV74KM72O2PEJN2C4XP3V5Q5MZUOO/
