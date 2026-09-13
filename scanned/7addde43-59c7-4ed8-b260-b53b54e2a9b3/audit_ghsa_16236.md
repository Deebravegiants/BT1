# [M] livehelperchat Server-Side Template Injection

## Summary
Severity: Medium
Advisory: GHSA-v4cp-2q7v-hg9q
CVE: CVE-2024-27516
Ecosystem: Packagist
Published: 2024-02-29
Source: https://github.com/advisories/GHSA-v4cp-2q7v-hg9q
Type: github-advisory

## Affected
- Packagist: `remdex/livehelperchat` — affected >=0 <4.29

## Details
Server-Side Template Injection (SSTI) vulnerability in livehelperchat before 4.34, allows remote attackers to execute arbitrary code and obtain sensitive information via the search parameter in lhc_web/modules/lhfaq/faqweight.php.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-27516
- https://github.com/LiveHelperChat/livehelperchat/issues/2054
- https://github.com/LiveHelperChat/livehelperchat/commit/a61d231526a36d4a7d8cc957914799ee1f9db0ab
- https://github.com/LiveHelperChat/livehelperchat
