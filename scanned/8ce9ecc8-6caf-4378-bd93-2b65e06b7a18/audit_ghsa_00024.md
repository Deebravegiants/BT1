# [C] Buffer Overflow in pycrypto

## Summary
Severity: Critical
Advisory: GHSA-cq27-v7xp-c356
CVE: CVE-2013-7459
CWE: CWE-119
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2018-12-14
Source: https://github.com/advisories/GHSA-cq27-v7xp-c356
Type: github-advisory

## Affected
- PyPI: `pycrypto` — affected >=0

## Details
Heap-based buffer overflow in the ALGnew function in block_templace.c in Python Cryptography Toolkit (aka pycrypto) allows remote attackers to execute arbitrary code as demonstrated by a crafted iv parameter to cryptmsg.py.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-7459
- https://github.com/dlitz/pycrypto/issues/176
- https://github.com/dlitz/pycrypto/commit/8dbe0dc3eea5c689d4f76b37b93fe216cf1f00d4
- https://bugzilla.redhat.com/show_bug.cgi?id=1409754
- https://github.com/advisories/GHSA-cq27-v7xp-c356
- https://github.com/dlitz/pycrypto
- https://github.com/pypa/advisory-database/tree/main/vulns/pycrypto/PYSEC-2017-94.yaml
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/C6BWNADPLKDBBQBUT3P75W7HAJCE7M3B
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/RJ37R2YLX56YZABFNAOWV4VTHTGYREAE
- https://security.gentoo.org/glsa/201702-14
- http://www.openwall.com/lists/oss-security/2016/12/27/8
