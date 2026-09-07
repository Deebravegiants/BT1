# [H] DataTable Vulnerable to Cross-Site Scripting

## Summary
Severity: High
Advisory: GHSA-4mv4-gmmf-q382
CVE: CVE-2015-6584
CWE: CWE-79
Ecosystem: Packagist, npm
Published: 2020-08-31
Source: https://github.com/advisories/GHSA-4mv4-gmmf-q382
Type: github-advisory

## Affected
- npm: `datatables` — affected >=0 <1.10.10
- Packagist: `datatables/datatables` — affected >=0 <1.10.10

## Details
Cross-site scripting (XSS) vulnerability in the DataTables plugin 1.10.8 and earlier for jQuery allows remote attackers to inject arbitrary web script or HTML via the scripts parameter to media/unit_testing/templates/6776.php.


## Recommendation

Update to a version greater than 1.10.8. A [fix](https://github.com/DataTables/DataTablesSrc/commit/ccf86dc5982bd8e16d) appears in [version 1.10.10](https://github.com/DataTables/DataTablesSrc/commits/1.10.10?after=9780a3693572757d87bf70e48bd7555faf974f28+34&branch=1.10.10&qualified_name=refs%2Ftags%2F1.10.10).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-6584
- https://github.com/DataTables/DataTables/issues/602
- https://github.com/DataTables/DataTablesSrc/commit/ccf86dc5982bd8e16d
- https://github.com/DataTables/DataTables
- https://github.com/DataTables/DataTablesSrc/commits/1.10.10?after=9780a3693572757d87bf70e48bd7555faf974f28+34&branch=1.10.10&qualified_name=refs%2Ftags%2F1.10.10
- https://www.netsparker.com/cve-2015-6384-xss-vulnerability-identified-in-datatables
- https://www.npmjs.com/advisories/5
- http://packetstormsecurity.com/files/133555/DataTables-1.10.8-Cross-Site-Scripting.html
- http://seclists.org/fulldisclosure/2015/Sep/37
- http://www.securityfocus.com/archive/1/536437/100/0/threaded
- http://www.securityfocus.com/archive/1/archive/1/536437/100/0/threaded
