# [M] Certifi removing TrustCor root certificate

## Summary
Severity: Medium
Advisory: GHSA-43fp-rhv2-5gv8
CVE: CVE-2022-23491
CWE: CWE-345
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:N/I:H/A:N (CVSS_V3)
Published: 2022-12-07
Source: https://github.com/advisories/GHSA-43fp-rhv2-5gv8
Type: github-advisory

## Affected
- PyPI: `certifi` — affected >=2017.11.05 <2022.12.07

## Details
Certifi 2022.12.07 removes root certificates from "TrustCor" from the root store. These are in the process of being removed from Mozilla's trust store.

TrustCor's root certificates are being removed pursuant to an investigation prompted by media reporting that TrustCor's ownership also operated a business that produced spyware. Conclusions of Mozilla's investigation can be found [here](https://groups.google.com/a/mozilla.org/g/dev-security-policy/c/oxX69KFvsm4/m/yLohoVqtCgAJ).

## References
- https://github.com/certifi/python-certifi/security/advisories/GHSA-43fp-rhv2-5gv8
- https://nvd.nist.gov/vuln/detail/CVE-2022-23491
- https://github.com/certifi/python-certifi/commit/9e9e840925d7b8e76c76fdac1fab7e6e88c1c3b8
- https://github.com/certifi/python-certifi
- https://github.com/pypa/advisory-database/tree/main/vulns/certifi/PYSEC-2022-42986.yaml
- https://groups.google.com/a/mozilla.org/g/dev-security-policy/c/oxX69KFvsm4/m/yLohoVqtCgAJ
- https://security.netapp.com/advisory/ntap-20230223-0010
