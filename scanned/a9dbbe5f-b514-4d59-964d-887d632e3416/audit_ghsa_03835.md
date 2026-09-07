# [H] Improper Encoding or Escaping of Output and Injection in LibreNMS

## Summary
Severity: High
Advisory: GHSA-w5r2-gvgf-mpm8
CVE: CVE-2019-12463
CWE: CWE-116, CWE-74
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2019-10-11
Source: https://github.com/advisories/GHSA-w5r2-gvgf-mpm8
Type: github-advisory

## Affected
- Packagist: `librenms/librenms` — affected >=1.50.1 <1.53

## Details
An issue was discovered in LibreNMS 1.50.1. The scripts that handle graphing options (includes/html/graphs/common.inc.php and includes/html/graphs/graphs.inc.php) do not sufficiently validate or encode several fields of user supplied input. Some parameters are filtered with mysqli_real_escape_string, which is only useful for preventing SQL injection attacks; other parameters are unfiltered. This allows an attacker to inject RRDtool syntax with newline characters via the html/graph.php and html/graph-realtime.php scripts. RRDtool syntax is quite versatile and an attacker could leverage this to perform a number of attacks, including disclosing directory structure and filenames, disclosing file content, denial of service, or writing arbitrary files. NOTE, relative to CVE-2019-10665, this requires authentication and the pathnames differ.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-12463
- https://www.darkmatter.ae/xen1thlabs/librenms-rrdtool-injection-vulnerability-xl-19-022
