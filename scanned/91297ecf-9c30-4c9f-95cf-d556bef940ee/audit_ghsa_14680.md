# [M] Jinja has a sandbox breakout through malicious filenames

## Summary
Severity: Medium
Advisory: GHSA-gmj6-6f8f-6699
CVE: CVE-2024-56201
CWE: CWE-150
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-12-23
Source: https://github.com/advisories/GHSA-gmj6-6f8f-6699
Type: github-advisory

## Affected
- PyPI: `jinja2` — affected >=3.0.0 <3.1.5

## Details
A bug in the Jinja compiler allows an attacker that controls both the content and filename of a template to execute arbitrary Python code, regardless of if Jinja's sandbox is used.

To exploit the vulnerability, an attacker needs to control both the filename and the contents of a template. Whether that is the case depends on the type of application using Jinja. This vulnerability impacts users of applications which execute untrusted templates where the template author can also choose the template filename.

## References
- https://github.com/pallets/jinja/security/advisories/GHSA-gmj6-6f8f-6699
- https://nvd.nist.gov/vuln/detail/CVE-2024-56201
- https://github.com/pallets/jinja/issues/1792
- https://github.com/pallets/jinja/commit/767b23617628419ae3709ccfb02f9602ae9fe51f
- https://github.com/pallets/jinja
- https://github.com/pallets/jinja/releases/tag/3.1.5
