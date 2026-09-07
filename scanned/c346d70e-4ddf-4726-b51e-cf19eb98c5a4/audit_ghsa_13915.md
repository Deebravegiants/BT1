# [M] Cross-site Scripting in UDX Stateless Media Plugin

## Summary
Severity: Medium
Advisory: GHSA-9j2p-8qqf-h55c
CVE: CVE-2022-4905
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-02-13
Source: https://github.com/advisories/GHSA-9j2p-8qqf-h55c
Type: github-advisory

## Affected
- Packagist: `wpcloud/wp-stateless` — affected >=0 <3.2.0

## Details
A vulnerability was found in UDX Stateless Media Plugin 3.1.1. It has been declared as problematic. This vulnerability affects the function setup_wizard_interface of the file lib/classes/class-settings.php. The manipulation of the argument settings leads to cross site scripting. The attack can be initiated remotely. Upgrading to version 3.2.0 is able to address this issue. The name of the patch is 6aee7ae0b0beeb2232ce6e1c82aa7e2041ae151a. It is recommended to upgrade the affected component. VDB-220750 is the identifier assigned to this vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-4905
- https://github.com/udx/wp-stateless/pull/630
- https://github.com/udx/wp-stateless/commit/6aee7ae0b0beeb2232ce6e1c82aa7e2041ae151a
- https://github.com/udx/wp-stateless
- https://github.com/udx/wp-stateless/releases/tag/3.2.0
- https://vuldb.com/?ctiid.220750
- https://vuldb.com/?id.220750
