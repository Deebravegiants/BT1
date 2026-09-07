# [M] ConcreteCMS Cross-Site Scripting (XSS) via HTML Block Text Field

## Summary
Severity: Medium
Advisory: GHSA-xfqf-5rhg-5c73
CVE: CVE-2025-2967
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2025-03-31
Source: https://github.com/advisories/GHSA-xfqf-5rhg-5c73
Type: github-advisory

## Affected
- Packagist: `concrete5/concrete5` — affected >=0

## Details
A vulnerability was found in ConcreteCMS up to 9.3.9. It has been classified as problematic. This affects the function Save of the component HTML Block Handler. The manipulation of the argument content leads to HTML injection. It is possible to initiate the attack remotely. The exploit has been disclosed to the public and may be used. The vendor was contacted early about this disclosure but did not respond in any way.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-2967
- https://github.com/concretecms/concretecms
- https://github.com/yaowenxiao721/Poc/blob/main/Concretecms/Concretecms-poc5.md
- https://vuldb.com/?ctiid.302019
- https://vuldb.com/?id.302019
- https://vuldb.com/?submit.522417
