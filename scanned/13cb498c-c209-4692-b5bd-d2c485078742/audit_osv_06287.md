# [H] BIT-libpython-2021-28861

## Summary
Severity: High
Advisory: BIT-libpython-2021-28861
Aliases: BIT-python-2021-28861, BIT-python-min-2021-28861, CVE-2021-28861, PSF-2022-5
Ecosystem: Bitnami
Published: 2025-08-11
Source: https://osv.dev/vulnerability/BIT-libpython-2021-28861
Type: osv

## Affected
- Bitnami: `libpython` — affected >=3.10.0 <3.10.6

## Details
Python 3.x through 3.10 has an open redirection vulnerability in lib/http/server.py due to no protection against multiple (/) at the beginning of URI path which may leads to information disclosure. NOTE: this is disputed by a third party because the http.server.html documentation page states "Warning: http.server is not recommended for production. It only implements basic security checks."

## References
- https://bugs.python.org/issue43223
- https://github.com/python/cpython/pull/24848
- https://github.com/python/cpython/pull/93879
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/2TRINJE3INWDVIHIABW4L2NP3RUSK7BJ/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/5LTSPFIULY2GZJN3QYNFVM4JSU6H4D6J/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/5OABQ5CMPQETJLFHROAXDIDXCMDTNVYG/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/DISZAFSIQ7IAPAEQTC7G2Z5QUA2V2PSW/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/HPX4XHT2FGVQYLY2STT2MRVENILNZTTU/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/I3MQT5ZE3QH5PVDJMERTBOCILHK35CBE/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/IFGV7P2PYFBMK32OKHCAC2ZPJQV5AUDF/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/KRGKPYA5YHIXQAMRIXO5DSCX7D4UUW4Q/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/OKYE2DOI2X7WZXAWTQJZAXYIWM37HDCY/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/QLE5INSVJUZJGY5OJXV6JREXWD7UDHYN/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/S7G66SRWUM36ENQ3X6LAIG7HAB27D4XJ/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/TZEPOPUFC42KXXSLFPZ47ZZRGPOR7SQE/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/WXF6MQ74HVIDDSR5AE2UDR24I6D4FEPC/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/X46T4EFTIBXZRYTGASBDEZGYJINH2OWV/
- https://nvd.nist.gov/vuln/detail/CVE-2021-28861
- https://security.gentoo.org/glsa/202305-02
- https://lists.debian.org/debian-lts-announce/2024/11/msg00024.html
