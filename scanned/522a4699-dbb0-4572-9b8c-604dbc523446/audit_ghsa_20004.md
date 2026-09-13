# [H] Passeo uses insecure random number generator

## Summary
Severity: High
Advisory: GHSA-mhhf-vgwh-fw9h
CVE: CVE-2022-23472
CWE: CWE-338
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-12-06
Source: https://github.com/advisories/GHSA-mhhf-vgwh-fw9h
Type: github-advisory

## Affected
- PyPI: `passeo` — affected >=0 <1.0.5

## Details
### Impact
Everyone below v1.0.5 is impacted by this flaw, of confidentiality being at risk due to the password(s) being easily able to be guessed with Passeo's use of the ``random`` library. It is recommended to change any passwords made with Passeo before v1.0.5 and upgrade to v1.0.5, and v1.0.5 patches this with the ``secrets`` library.

### Workarounds
No current workaround available than updating to v1.0.5.

## References
- https://github.com/ArjunSharda/Passeo/security/advisories/GHSA-mhhf-vgwh-fw9h
- https://nvd.nist.gov/vuln/detail/CVE-2022-23472
- https://github.com/ArjunSharda/Passeo/commit/8caa798b6bc4647dca59b2376204b6dc6176361a
- https://github.com/ArjunSharda/Passeo
- https://github.com/pypa/advisory-database/tree/main/vulns/passeo/PYSEC-2022-42997.yaml
- https://peps.python.org/pep-0506
