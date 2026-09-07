# [M] The mailqueue TYPO3 extension has Insecure Deserialization in `TransportFailure` class

## Summary
Severity: Medium
Advisory: GHSA-2pm6-9fhx-vvg3
CVE: CVE-2026-1323
CWE: CWE-502
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-03-18
Source: https://github.com/advisories/GHSA-2pm6-9fhx-vvg3
Type: github-advisory

## Affected
- Packagist: `cpsit/typo3-mailqueue` — affected >=0 <0.4.5
- Packagist: `cpsit/typo3-mailqueue` — affected >=0.5.0 <0.5.2

## Details
## Description

The extension fails to properly define allowed classes used when deserializing transport failure metadata. An attacker may exploit this to execute untrusted serialized code. Note that an active exploit requires write access to the directory configured at `$GLOBALS['TYPO3_CONF_VARS']['MAIL']['transport_spool_filepath']`.

## References
- https://github.com/CPS-IT/mailqueue/security/advisories/GHSA-2pm6-9fhx-vvg3
- https://nvd.nist.gov/vuln/detail/CVE-2026-1323
- https://github.com/CPS-IT/mailqueue/commit/0f7a1376bbbd8c7658030d02e51c10a85b1dfdf7
- https://github.com/CPS-IT/mailqueue/commit/600c7dba99f8eea5f2505b848ee3dd4713440741
- https://github.com/CPS-IT/mailqueue
- https://typo3.org/security/advisory/typo3-ext-sa-2026-005
