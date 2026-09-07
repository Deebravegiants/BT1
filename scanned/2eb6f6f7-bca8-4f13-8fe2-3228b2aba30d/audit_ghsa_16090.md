# [M] OctoPrint Vulnerable to Reflected XSS in Jinja2 Templates

## Summary
Severity: Medium
Advisory: GHSA-xvxq-g8hw-fx4g
CVE: CVE-2024-49377
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:A/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2024-11-05
Source: https://github.com/advisories/GHSA-xvxq-g8hw-fx4g
Type: github-advisory

## Affected
- PyPI: `OctoPrint` — affected >=0 <1.10.3

## Details
### Impact

OctoPrint versions up until and including 1.10.2 are vulnerable to reflected XSS vulnerabilities through its Jinja2 template system, as this is not configured to enforce automatic escaping. This affects, among other places, the login dialog and the standalone application key confirmation dialog. 

An attacker who successfully talked a victim into clicking on or through a malicious third party app successfully redirected a victim to a specially crafted link could use this to retrieve or modify sensitive configuration settings, interrupt prints or otherwise interact with the OctoPrint instance in a malicious way.

### Patches

The above mentioned specific vulnerabilities of the login dialog and the standalone application key confirmation dialog will be patched in the bugfix release 1.10.3 by individual escaping of the detected locations. A global change throughout all of OctoPrint's templating system with the upcoming 1.11.0 release will handle this further, switching to globally enforced automatic escaping and thus reducing the attack surface in general.

The latter will also improve the security of third party plugins. During a transition period, third party plugins will be able to opt into the automatic escaping. With OctoPrint 1.13.0, automatic escaping will be switched over to be enforced even for third party plugins, unless they explicitly opt-out.

### Credits

This vulnerability was discovered and responsibly disclosed to OctoPrint by Jacopo Tediosi.

## References
- https://github.com/OctoPrint/OctoPrint/security/advisories/GHSA-xvxq-g8hw-fx4g
- https://nvd.nist.gov/vuln/detail/CVE-2024-49377
- https://github.com/OctoPrint/OctoPrint/commit/b8a6b0a75202edac3bb142a8e4f9041a0b6825bf
- https://github.com/OctoPrint/OctoPrint
- https://github.com/pypa/advisory-database/tree/main/vulns/octoprint/PYSEC-2024-201.yaml
