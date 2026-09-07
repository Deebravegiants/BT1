# [M] Jupyter Server has an open redirection vulnerability in `next` query parameter

## Summary
Severity: Medium
Advisory: GHSA-qh7q-6qm3-653w
CVE: CVE-2025-61669
CWE: CWE-601
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:P/VC:N/VI:N/VA:N/SC:H/SI:N/SA:N (CVSS_V4)
Published: 2026-05-05
Source: https://github.com/advisories/GHSA-qh7q-6qm3-653w
Type: github-advisory

## Affected
- PyPI: `jupyter-server` — affected >=0 <2.18.0

## Details
### Summary

The `?next=...` URL query parameter has an open redirection vulnerability. In `jupyter_server<=2.17.0`, this URL query parameter allows redirection to arbitrary external domains, which can be exploited to facilitate phishing attacks on server users.

### Details

The vulnerability is caused by insufficient validation in the `LoginFormHandler._redirect_safe()` method.

- Source code reference: https://github.com/jupyter-server/jupyter_server/blob/987ebdd5e188cdc49751b01a0d6782d686492a53/jupyter_server/auth/login.py#L33-L76

This vulnerability was originally reported by Noriaki Iwasaki. All discovery credit goes to them.

### PoC

1. Navigate to `http://localhost:8888/login?next=///google.com`
2. Observe that the user is redirected to `google.com` despite it being an external domain.

The external domain passed in the `?next` parameter may be replaced with a malicious lookalike to facilitate phishing attacks. Jupyter Server deployments served on a public domain are especially vulnerable, as `prod.company.com` may be redirected to a look-alike URL such as `prod.company.dev`. 

### Impact

This vulnerability affects all users, especially enterprise users who work with sensitive/confidential data.

### Patches

Jupyter Server 2.18+

### Workaround

None.

## References
- https://github.com/jupyter-server/jupyter_server/security/advisories/GHSA-qh7q-6qm3-653w
- https://nvd.nist.gov/vuln/detail/CVE-2025-61669
- https://github.com/jupyter-server/jupyter_server
- https://github.com/pypa/advisory-database/tree/main/vulns/jupyter-server/PYSEC-2026-67.yaml
