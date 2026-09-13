# [H] Signify allows a remote attacker to escalate privileges via the signed_data.py and the context.py components

## Summary
Severity: High
Advisory: GHSA-p4hh-mq57-gq8x
CVE: CVE-2025-70887
CWE: CWE-269
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:L/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-25
Source: https://github.com/advisories/GHSA-p4hh-mq57-gq8x
Type: github-advisory

## Affected
- PyPI: `signify` — affected >=0 <0.9.2

## Details
An issue in ralphje Signify before v.0.9.2 allows a remote attacker to escalate privileges via the signed_data.py and the context.py components

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-70887
- https://github.com/mtrojnar/osslsigncode/issues/475
- https://github.com/ralphje/signify/issues/60
- https://github.com/mtrojnar/osslsigncode/pull/477
- https://github.com/ralphje/signify/commit/64f21c0cc06cea0536370686ca3ba7a01e4adaa8
- https://github.com/mtrojnar/osslsigncode/releases/tag/2.11
- https://github.com/ralphje/signify
