# [M] Weblate: SSRF via Project-Level Machinery Configuration 

## Summary
Severity: Medium
Advisory: GHSA-xrwr-fcw6-fmq8
CVE: CVE-2026-34244
CWE: CWE-200, CWE-918
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:N/A:N (CVSS_V3)
Published: 2026-04-16
Source: https://github.com/advisories/GHSA-xrwr-fcw6-fmq8
Type: github-advisory

## Affected
- PyPI: `weblate` — affected >=0 <5.17

## Details
### Impact
A user with the `project.edit` permission (granted by the per-project "Administration" role) can configure machine translation service URLs pointing to arbitrary internal network addresses. During configuration validation, Weblate makes an HTTP request to the attacker-controlled URL and reflects up to 200 characters of the response body back to the user in an error message. This constitutes a Server-Side Request Forgery (SSRF) with partial response read.

### Patches

* https://github.com/WeblateOrg/weblate/pull/18684
* The solution then has been cleaned up in followup patches

### Workarounds
Limiting available machinery services via WEBLATE_MACHINERY setting can avoid this.

### References

Thanks to @DavidCarliez for disclosing this via GitHub private vulnerability reporting.

## References
- https://github.com/WeblateOrg/weblate/security/advisories/GHSA-xrwr-fcw6-fmq8
- https://nvd.nist.gov/vuln/detail/CVE-2026-34244
- https://github.com/WeblateOrg/weblate/pull/18684
- https://github.com/WeblateOrg/weblate/commit/e619e9090202e4886b844c110d39308e7e882c0e
- https://github.com/WeblateOrg/weblate
