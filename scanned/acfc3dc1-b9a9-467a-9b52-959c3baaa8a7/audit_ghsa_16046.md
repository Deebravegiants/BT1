# [M] OctoPrint has API key access in settings without reauthentication

## Summary
Severity: Medium
Advisory: GHSA-cc6x-8cc7-9953
CVE: CVE-2024-51493
CWE: CWE-306, CWE-620
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2024-11-05
Source: https://github.com/advisories/GHSA-cc6x-8cc7-9953
Type: github-advisory

## Affected
- PyPI: `OctoPrint` — affected >=0 <1.10.3

## Details
### Impact

OctoPrint versions up until and including 1.10.2 contain a vulnerability that allows an attacker that has gained temporary control over an authenticated victim's OctoPrint browser session to retrieve/recreate/delete the user's or - if the victim has admin permissions - the global API key without having to reauthenticate by re-entering the user account's password. 

An attacker could use a stolen API key to access OctoPrint through its API, or disrupt workflows depending on the API key they deleted.

### Patches

The vulnerability will be patched in version 1.10.3.

### Credits

This vulnerability was discovered and responsibly disclosed to OctoPrint by Jacopo Tediosi.

## References
- https://github.com/OctoPrint/OctoPrint/security/advisories/GHSA-cc6x-8cc7-9953
- https://nvd.nist.gov/vuln/detail/CVE-2024-51493
- https://github.com/OctoPrint/OctoPrint/commit/9bc80d782d72881b16e20873dcd0b8314324c70c
- https://github.com/OctoPrint/OctoPrint
- https://github.com/pypa/advisory-database/tree/main/vulns/octoprint/PYSEC-2024-202.yaml
