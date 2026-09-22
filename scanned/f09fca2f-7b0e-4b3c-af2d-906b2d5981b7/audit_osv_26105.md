# [H] Improper Path Sanitization in JSON Datasource Plugin

## Summary
Severity: High
Advisory: CVE-2023-5123
CVSS: 8.0 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H)
Published: 2024-02-14
Source: https://osv.dev/vulnerability/CVE-2023-5123
Type: osv

## Details
The JSON datasource plugin ( https://grafana.com/grafana/plugins/marcusolsson-json-datasource/ ) is a Grafana Labs maintained plugin for Grafana that allows for retrieving and processing JSON data from a remote endpoint (including a specific sub-path) configured by an administrator. Due to inadequate sanitization of the dashboard-supplied path parameter, it was possible to include path traversal characters (../) in the path parameter and send requests to paths on the configured endpoint outside the configured sub-path. 





    
    
            






    
    
            This means that if the datasource was configured by an administrator to point at some sub-path of a domain (e.g.  https://example.com/api/some_safe_api/ ), it was possible for an editor to create a dashboard referencing the datasource which issues queries containing path traversal characters, which would in turn cause the datasource to instead query arbitrary subpaths on the configured domain (e.g.  https://example.com/api/admin_api/) .

In the rare case that this plugin is configured by an administrator to point back at the Grafana instance itself, this vulnerability becomes considerably more severe, as an administrator browsing a maliciously configured panel could be compelled to make requests to Grafana administrative API endpoints with their credentials, resulting in the potential for privilege escalation, hence the high score for this vulnerability.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/5xxx/CVE-2023-5123.json
- https://grafana.com/security/security-advisories/cve-2023-5123/
- https://nvd.nist.gov/vuln/detail/CVE-2023-5123
- https://security.netapp.com/advisory/ntap-20240503-0007/
- https://github.com/grafana/grafana-json-datasource
