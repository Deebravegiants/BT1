# [M] PyCrypto makes Use of Insufficiently Random Values

## Summary
Severity: Medium
Advisory: GHSA-v367-p58w-98h5
CVE: CVE-2012-2417
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-v367-p58w-98h5
Type: github-advisory

## Affected
- PyPI: `PyCrypto` — affected >=0 <2.6

## Details
PyCrypto before 2.6 does not produce appropriate prime numbers when using an ElGamal scheme to generate a key, which reduces the signature space or public key space and makes it easier for attackers to conduct brute force attacks to obtain the private key.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2012-2417
- https://github.com/Legrandin/pycrypto/commit/9f912f13df99ad3421eff360d6a62d7dbec755c2
- https://bugs.launchpad.net/pycrypto/+bug/985164
- https://exchange.xforce.ibmcloud.com/vulnerabilities/75871
- https://github.com/Legrandin/pycrypto
- https://github.com/dlitz/pycrypto/blob/373ea760f21701b162e8c4912a66928ee30d401a/ChangeLog
- https://github.com/pypa/advisory-database/tree/main/vulns/pycrypto/PYSEC-2012-16.yaml
- https://hermes.opensuse.org/messages/15083589
- https://web.archive.org/web/20140724111917/http://secunia.com/advisories/49263
- https://web.archive.org/web/20200228184120/http://www.securityfocus.com/bid/53687
- http://lists.fedoraproject.org/pipermail/package-announce/2012-June/081713.html
- http://lists.fedoraproject.org/pipermail/package-announce/2012-June/081759.html
- http://lists.fedoraproject.org/pipermail/package-announce/2012-June/081789.html
- http://www.debian.org/security/2012/dsa-2502
- http://www.mandriva.com/security/advisories?name=MDVSA-2012:117
- http://www.openwall.com/lists/oss-security/2012/05/25/1
