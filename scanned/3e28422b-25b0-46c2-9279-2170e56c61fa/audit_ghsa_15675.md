# [M] Bolt CMS Cross-site Scripting vulnerability

## Summary
Severity: Medium
Advisory: GHSA-xhqw-4hcq-fcvr
CVE: CVE-2024-7300
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2024-07-31
Source: https://github.com/advisories/GHSA-xhqw-4hcq-fcvr
Type: github-advisory

## Affected
- Packagist: `bolt/bolt` — affected >=0

## Details
** UNSUPPORTED WHEN ASSIGNED ** A vulnerability classified as problematic has been found in Bolt CMS 3.7.1. Affected is an unknown function of the file /bolt/editcontent/showcases of the component Showcase Creation Handler. The manipulation of the argument textarea leads to cross site scripting. It is possible to launch the attack remotely. The exploit has been disclosed to the public and may be used. The identifier of this vulnerability is VDB-273168. NOTE: This vulnerability only affects products that are no longer supported by the maintainer. NOTE: Vendor was contacted early and confirmed that the affected release tree is end-of-life.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-7300
- https://github.com/bolt/bolt
- https://vuldb.com/?ctiid.273168
- https://vuldb.com/?id.273168
- https://vuldb.com/?submit.380678
