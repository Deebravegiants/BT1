# [H] Froxlor PHP Object Injection vulnerability

## Summary
Severity: High
Advisory: GHSA-g77v-m226-3f7g
CVE: CVE-2018-1000527
CWE: CWE-502
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-g77v-m226-3f7g
Type: github-advisory

## Affected
- Packagist: `froxlor/froxlor` — affected >=0 <0.9.40

## Details
Froxlor version <= 0.9.39.5 contains a PHP Object Injection vulnerability in Domain name form that can result in Possible information disclosure and remote code execution. This attack appear to be exploitable via Passing malicious PHP objection in $_POST['ssl_ipandport']. This vulnerability appears to have been fixed in after commit c1e62e6.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1000527
- https://github.com/Froxlor/Froxlor/issues/555
- https://github.com/Froxlor/Froxlor/commit/c1e62e6be719affc003774a639de5c952ffd8ffc
- https://0dd.zone/2018/05/31/Froxlor-Object-Injection
- https://github.com/Froxlor/Froxlor
