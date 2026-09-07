# [M] Session key exposure through session list in Django User Sessions

## Summary
Severity: Medium
Advisory: GHSA-5fq8-3q2f-4m5g
CVE: CVE-2020-5224
CWE: CWE-287
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:C/C:H/I:L/A:N (CVSS_V3)
Published: 2020-01-24
Source: https://github.com/advisories/GHSA-5fq8-3q2f-4m5g
Type: github-advisory

## Affected
- PyPI: `django-user-sessions` — affected >=0 <1.7.1

## Details
### Impact
The views provided by django-user-sessions allow users to terminate specific sessions. The session key is used to identify sessions, and thus included in the rendered HTML. In itself this is not a problem. However if the website has an XSS vulnerability, the session key could be extracted by the attacker and a session takeover could happen.

### Patches
Patch is under way.

### Workarounds
Remove the session_key from the template.

### References
_None._

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [Bouke/django-user-sessions](https://github.com/Bouke/django-user-sessions/issues)
* Email us at [bouke@haarsma.eu](mailto:bouke@haarsma.eu)

## References
- https://github.com/Bouke/django-user-sessions/security/advisories/GHSA-5fq8-3q2f-4m5g
- https://nvd.nist.gov/vuln/detail/CVE-2020-5224
- https://github.com/jazzband/django-user-sessions/commit/f0c4077e7d1436ba6d721af85cee89222ca5d2d9
- https://github.com/Bouke/django-user-sessions
- https://github.com/pypa/advisory-database/tree/main/vulns/django-user-sessions/PYSEC-2020-230.yaml
