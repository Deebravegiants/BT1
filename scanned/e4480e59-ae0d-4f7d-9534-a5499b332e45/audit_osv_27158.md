# [C] ProjectSend Unauthenticated Configuration Modification

## Summary
Severity: Critical
Advisory: CVE-2024-11680
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-11-26
Source: https://osv.dev/vulnerability/CVE-2024-11680
Type: osv

## Details
ProjectSend versions prior to r1720 are affected by an improper authentication vulnerability. Remote, unauthenticated attackers can exploit this flaw by sending crafted HTTP requests to options.php, enabling unauthorized modification of the application's configuration. Successful exploitation allows attackers to create accounts, upload webshells, and embed malicious JavaScript.

## References
- https://www.cisa.gov/known-exploited-vulnerabilities-catalog?field_cve=CVE-2024-11680
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/11xxx/CVE-2024-11680.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-11680
- https://vulncheck.com/advisories/projectsend-bypass
- https://github.com/projectsend/projectsend/commit/193367d937b1a59ed5b68dd4e60bd53317473744
- https://github.com/projectsend/projectsend
- https://github.com/projectdiscovery/nuclei-templates/blob/main/http/vulnerabilities/projectsend-auth-bypass.yaml
- https://github.com/rapid7/metasploit-framework/blob/master/modules/exploits/linux/http/projectsend_unauth_rce.rb
- https://www.synacktiv.com/sites/default/files/2024-07/synacktiv-projectsend-multiple-vulnerabilities.pdf
