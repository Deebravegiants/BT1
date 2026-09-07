# [M] Nautobot vulnerable to secrets exposure and data manipulation through Jinja2 templating

## Summary
Severity: Medium
Advisory: GHSA-wjw6-95h5-4jpx
CVE: CVE-2025-49142
CWE: CWE-1336
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:H/AT:N/PR:L/UI:N/VC:H/VI:L/VA:N/SC:L/SI:L/SA:L (CVSS_V4)
Published: 2025-06-10
Source: https://github.com/advisories/GHSA-wjw6-95h5-4jpx
Type: github-advisory

## Affected
- PyPI: `nautobot` — affected >=0 <1.6.32
- PyPI: `nautobot` — affected >=2.0.0 <2.4.10

## Details
### Impact
_What kind of vulnerability is it? Who is impacted?_

All users of Nautobot versions prior to 2.4.10 or prior to 1.6.32 are potentially affected.

Due to insufficient security configuration of the Jinja2 templating feature used in computed fields, custom links, etc. in Nautobot:

1. A malicious user could configure this feature set in ways that could expose the value of Secrets defined in Nautobot when the templated content is rendered.
2. A malicious user could configure this feature set in ways that could call Python APIs to modify data within Nautobot when the templated content is rendered, bypassing the object permissions assigned to the viewing user.

### Patches
_Has the problem been patched? What versions should users upgrade to?_

Nautobot versions 1.6.32 and 2.4.10 will include fixes for the vulnerability.

### Workarounds
_Is there a way for users to fix or remediate the vulnerability without upgrading?_

The vulnerability can be partially mitigated by configuring object permissions appropriately to limit the below actions to only trusted users:

- `extras.add_secret`
- `extras.change_secret`
- `extras.view_secret`
- `extras.add_computedfield`
- `extras.change_computedfield`
- `extras.add_customlink`
- `extras.change_customlink`
- `extras.add_jobbutton`
- `extras.change_jobbutton`

### References
_Are there any links users can visit to find out more?_

- https://jinja.palletsprojects.com/en/stable/sandbox/
- https://docs.djangoproject.com/en/4.2/ref/templates/api/#alters-data-description
- https://github.com/nautobot/nautobot/pull/7417
- https://github.com/nautobot/nautobot/pull/7429

## References
- https://github.com/nautobot/nautobot/security/advisories/GHSA-wjw6-95h5-4jpx
- https://nvd.nist.gov/vuln/detail/CVE-2025-49142
- https://github.com/nautobot/nautobot/pull/7417
- https://github.com/nautobot/nautobot/pull/7429
- https://docs.djangoproject.com/en/4.2/ref/templates/api/#alters-data-description
- https://github.com/nautobot/nautobot
- https://github.com/pypa/advisory-database/tree/main/vulns/jinja2/PYSEC-2025-74.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/nautobot/PYSEC-2025-79.yaml
- https://jinja.palletsprojects.com/en/stable/sandbox
