# [M] Weblate has a Server-Side Request Forgery issue

## Summary
Severity: Medium
Advisory: GHSA-hfpv-mc5v-p9mm
CVE: CVE-2025-66407
CWE: CWE-352, CWE-918
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:N/A:N (CVSS_V3)
Published: 2026-05-26
Source: https://github.com/advisories/GHSA-hfpv-mc5v-p9mm
Type: github-advisory

## Affected
- PyPI: `Weblate` — affected >=0 <5.15

## Details
### Impact
The Create Component functionality in Weblate allows authorized users to add new translation components by specifying both a version control system and a source code repository URL to pull from. However, the repository URL field is not validated or sanitized, allowing an attacker to supply arbitrary protocols, hostnames, and IP addresses, including localhost, internal network addresses, and local filenames.

When the Mercurial version control system is selected, Weblate exposes the full server-side HTTP response for the provided URL. This effectively creates a server-side request forgery (SSRF) primitive that can probe internal services and return their contents. In addition to accessing internal HTTP endpoints, the behavior also enables local file enumeration by attempting file:// requests. While file contents may not always be returned, the application’s error messages clearly differentiate between files that exist and files that do not, revealing information about the server’s filesystem layout.



In cloud environments, this behavior is particularly dangerous, as internal-only endpoints such as cloud metadata services may be accessible, potentially leading to credential disclosure and full environment compromise.

### Patches

This has been addressed in the Weblate 5.15 release.

* https://github.com/WeblateOrg/weblate/pull/17103
* https://github.com/WeblateOrg/weblate/pull/17102

### Workarounds

Removing Mercurial from [VCS_BACKENDS](https://docs.weblate.org/en/latest/admin/config.html#vcs-backends) avoids this vulnerability, as the Git backend is not affected. The Git backend was already configured to block the file protocol and does not expose the HTTP response content in the error message.

### References
Thanks to Jason Marcello for responsible disclosure.

## References
- https://github.com/WeblateOrg/weblate/security/advisories/GHSA-hfpv-mc5v-p9mm
- https://nvd.nist.gov/vuln/detail/CVE-2025-66407
- https://github.com/WeblateOrg/weblate/pull/17102
- https://github.com/WeblateOrg/weblate/pull/17103
- https://github.com/WeblateOrg/weblate
- https://github.com/pypa/advisory-database/tree/main/vulns/weblate/PYSEC-2025-231.yaml
