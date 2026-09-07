# [H] MobSF allows attackers to read arbitrary files via a crafted HTTP request

## Summary
Severity: High
Advisory: GHSA-f42p-vc8p-7x54
CVE: CVE-2022-41547
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-10-18
Source: https://github.com/advisories/GHSA-f42p-vc8p-7x54
Type: github-advisory

## Affected
- PyPI: `mobsf` — affected >=0 <0.9.3

## Details
Mobile Security Framework (MobSF) v0.9.2 and below was discovered to contain a local file inclusion (LFI) vulnerability in the `StaticAnalyzer/views.py` script. This vulnerability allows attackers to read arbitrary files via a crafted HTTP request.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-41547
- https://github.com/MobSF/Mobile-Security-Framework-MobSF/pull/166
- https://github.com/MobSF/Mobile-Security-Framework-MobSF/commit/b9cdd1f52bdf127cf33bb1be369e374a2855f8e6#diff-69d2e38f6bba208c333da6a09a83ca65056fcb60f4e10d23f67c01bcc1ffb58c
- https://github.com/MobSF/Mobile-Security-Framework-MobSF
