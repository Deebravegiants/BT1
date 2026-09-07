# [M] Nautobot Single Source of Truth (SSoT) has an unauthenticated ServiceNow configuration URL

## Summary
Severity: Medium
Advisory: GHSA-535g-62r7-cx6v
CVE: CVE-2025-62607
CWE: CWE-306
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2025-10-21
Source: https://github.com/advisories/GHSA-535g-62r7-cx6v
Type: github-advisory

## Affected
- PyPI: `nautobot-ssot` — affected >=0 <3.10.0

## Details
The servicenow config URL is using a generic django View with no authentication.

URL: `/plugins/ssot/servicenow/config/`

### Impact
_What kind of vulnerability is it? Who is impacted?_
An Unauthenticated attacker could access this page to view the Service Now public instance name e.g. `companyname.service-now.com`. This is considered **low-value information**.  This does not expose the Secret, the Secret Name, or the Secret Value for the Username/Password for Service-Now.com. An unauthenticated member would not be able to change the instance name, nor set a Secret. There is not a way to gain access to other pages Nautobot through the unauthenticated Configuration page.

### Patches
_Has the problem been patched? What versions should users upgrade to?_
We highly recommend upgrading to SSoT v3.10.0 which includes this patch.

### Workarounds
_Is there a way for users to fix or remediate the vulnerability without upgrading?_
Disable the servicenow SSoT integration

## References
- https://github.com/nautobot/nautobot-app-ssot/security/advisories/GHSA-535g-62r7-cx6v
- https://nvd.nist.gov/vuln/detail/CVE-2025-62607
- https://github.com/nautobot/nautobot-app-ssot/commit/1530d25cdeb929641ec47644f9a0a1d9d41e1cb8
- https://github.com/nautobot/nautobot-app-ssot
- https://github.com/nautobot/nautobot-app-ssot/releases/tag/v3.10.0
