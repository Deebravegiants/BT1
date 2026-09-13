# [M] SleekXMPP and Slixmpp Incorrect Implementation of Message Carbons 

## Summary
Severity: Medium
Advisory: GHSA-c35g-jr5f-h83p
CVE: CVE-2017-5591
CWE: CWE-940
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-c35g-jr5f-h83p
Type: github-advisory

## Affected
- PyPI: `slixmpp` — affected >=0 <1.2.4
- PyPI: `SleekXMPP` — affected >=0 <1.3.2

## Details
An incorrect implementation of "XEP-0280: Message Carbons" in multiple XMPP clients allows a remote attacker to impersonate any user, including contacts, in the vulnerable application's display. This allows for various kinds of social engineering attacks. This CVE is for SleekXMPP up to 1.3.1 and Slixmpp all versions up to 1.2.3, as bundled in poezio (0.8 - 0.10) and other products.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-5591
- https://github.com/fritzy/SleekXMPP/issues/442
- https://github.com/fritzy/SleekXMPP/commit/285495d5ee2427d93d961ceedcd1829383e5196d
- https://github.com/poezio/slixmpp/commit/22664ee7b86c8e010f312b66d12590fb47160ad8
- https://github.com/poezio/slixmpp
- https://github.com/pypa/advisory-database/tree/main/vulns/sleekxmpp/PYSEC-2017-103.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/slixmpp/PYSEC-2017-104.yaml
- https://pypi.org/project/sleekxmpp
- https://pypi.org/project/slixmpp
- https://rt-solutions.de/en/2017/02/CVE-2017-5589_xmpp_carbons
- https://rt-solutions.de/wp-content/uploads/2017/02/CVE-2017-5589_xmpp_carbons.pdf
- https://web.archive.org/web/20200227192025/http://www.securityfocus.com/bid/96166
- http://openwall.com/lists/oss-security/2017/02/09/29
