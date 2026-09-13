# [M] Nautobot dynamic-group-members doesn't enforce permission restrictions on member objects

## Summary
Severity: Medium
Advisory: GHSA-qmjf-wc2h-6x3q
CVE: CVE-2024-36112
CWE: CWE-280
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2024-05-29
Source: https://github.com/advisories/GHSA-qmjf-wc2h-6x3q
Type: github-advisory

## Affected
- PyPI: `nautobot` — affected >=1.3.0 <1.6.23
- PyPI: `nautobot` — affected >=2.0.0 <2.2.5

## Details
### Impact
_What kind of vulnerability is it? Who is impacted?_

A user with permissions to view Dynamic Group records (`extras.view_dynamicgroup` permission) can use the Dynamic Group detail UI view (`/extras/dynamic-groups/<uuid>/`) and/or the members REST API view (`/api/extras/dynamic-groups/<uuid>/members/`) to list the objects that are members of a given Dynamic Group. 

In versions of Nautobot between 1.3.0 (where the Dynamic Groups feature was added) and 1.6.22 inclusive, and 2.0.0 through 2.2.4 inclusive, Nautobot fails to restrict these listings based on the member object permissions - for example a Dynamic Group of Device objects will list all Devices that it contains, regardless of the user's `dcim.view_device` permissions or lack thereof.

### Patches
_Has the problem been patched? What versions should users upgrade to?_

Fixed in Nautobot 1.6.23 and 2.2.5.

### Workarounds
_Is there a way for users to fix or remediate the vulnerability without upgrading?_

This vulnerability can be partially mitigated by removing `extras.view_dynamicgroup` permission from users; a full fix will require upgrading.

### References
_Are there any links users can visit to find out more?_

- https://github.com/nautobot/nautobot/pull/5757
- https://github.com/nautobot/nautobot/pull/5762

## References
- https://github.com/nautobot/nautobot/security/advisories/GHSA-qmjf-wc2h-6x3q
- https://nvd.nist.gov/vuln/detail/CVE-2024-36112
- https://github.com/nautobot/nautobot/pull/5757
- https://github.com/nautobot/nautobot/pull/5762
- https://github.com/nautobot/nautobot/commit/3a63aa1327f943b2ac8452757ea2e4d403387ad6
- https://github.com/nautobot/nautobot/commit/4d1ff2abe2775b0a6fb16e6d1d503a78226a6f8e
- https://github.com/nautobot/nautobot
- https://github.com/pypa/advisory-database/tree/main/vulns/nautobot/PYSEC-2024-166.yaml
