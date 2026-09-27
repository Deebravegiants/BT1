# [H] PyFriBidi Buffer overflow in the fribidi_utf8_to_unicode function

## Summary
Severity: High
Advisory: GHSA-6476-g47x-h3c7
CVE: CVE-2012-1176
CWE: CWE-119
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-6476-g47x-h3c7
Type: github-advisory

## Affected
- PyPI: `pyfribidi` — affected >=0 <0.11.0

## Details
Buffer overflow in the fribidi_utf8_to_unicode function in PyFriBidi before 0.11.0 allows remote attackers to cause a denial of service (application crash) via a 4-byte utf-8 sequence.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2012-1176
- https://github.com/pediapress/pyfribidi/issues/2
- https://github.com/pediapress/pyfribidi/issues/2%29:
- https://github.com/pediapress/pyfribidi/commit/d2860c655357975e7b32d84e6b45e98f0dcecd7a
- https://bugzilla.redhat.com/show_bug.cgi?id=801896
- https://bugzilla.wikimedia.org/show_bug.cgi?id=35055
- https://exchange.xforce.ibmcloud.com/vulnerabilities/74001
- https://github.com/pediapress/pyfribidi
- https://github.com/pypa/advisory-database/tree/main/vulns/pyfribidi/PYSEC-2012-11.yaml
- https://web.archive.org/web/20200228170815/http://www.securityfocus.com/bid/52451
- http://bugs.debian.org/cgi-bin/bugreport.cgi?bug=663189
- http://groups.google.com/group/linux.debian.bugs.dist/browse_thread/thread/aacd036037217998/8d095f85f3665bff?lnk=raot
- http://lists.fedoraproject.org/pipermail/package-announce/2012-March/075293.html
- http://lists.fedoraproject.org/pipermail/package-announce/2012-March/076038.html
- http://lists.fedoraproject.org/pipermail/package-announce/2012-March/076053.html
- http://www.openwall.com/lists/oss-security/2012/03/14/4
- http://www.openwall.com/lists/oss-security/2012/03/14/9
