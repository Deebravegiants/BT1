# [H] Code injection in FreeIPA

## Summary
Severity: High
Advisory: GHSA-7hpj-hfcr-5qwm
CVE: CVE-2019-14867
CWE: CWE-400, CWE-94
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-12-06
Source: https://github.com/advisories/GHSA-7hpj-hfcr-5qwm
Type: github-advisory

## Affected
- PyPI: `ipa` — affected >=4.6.2 <4.6.7
- PyPI: `ipa` — affected >=4.7.0 <4.7.4
- PyPI: `ipa` — affected >=4.8.0 <4.8.3
- PyPI: `freeipa` — affected >=4.6.2 <4.6.7
- PyPI: `freeipa` — affected >=4.7.0 <4.7.4
- PyPI: `freeipa` — affected >=4.8.0 <4.8.3

## Details
A flaw was found in IPA, all 4.6.x versions before 4.6.7, all 4.7.x versions before 4.7.4 and all 4.8.x versions before 4.8.3, in the way the internal function ber_scanf() was used in some components of the IPA server, which parsed kerberos key data. An unauthenticated attacker who could trigger parsing of the krb principal key could cause the IPA server to crash or in some conditions, cause arbitrary code to be executed on the server hosting the IPA server.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-14867
- https://access.redhat.com/errata/RHBA-2019:4268
- https://access.redhat.com/errata/RHSA-2020:0378
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2019-14867
- https://github.com/advisories/GHSA-7hpj-hfcr-5qwm
- https://github.com/pypa/advisory-database/tree/main/vulns/ipa/PYSEC-2019-28.yaml
- https://github.com/pypa/advisory-db/tree/main/vulns/ipa/PYSEC-2019-28.yaml
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/67SEUWJAJ5RMH5K4Q6TS2I7HIMXUGNKF
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/WLFL5XDCJ3WT6JCLCQVKHZBLHGW7PW4T
- https://www.freeipa.org/page/Releases/4.6.7
- https://www.freeipa.org/page/Releases/4.7.4
- https://www.freeipa.org/page/Releases/4.8.3
