# [H] LDAP password exposure in glpi

## Summary
Severity: High
Advisory: CVE-2022-24867
Aliases: GHSA-4r49-52q9-5fgr
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2022-04-21
Source: https://osv.dev/vulnerability/CVE-2022-24867
Type: osv

## Details
GLPI is a Free Asset and IT Management Software package, that provides ITIL Service Desk features, licenses tracking and software auditing. When you pass the config to the javascript, some entries are filtered out. The variable ldap_pass is not filtered and when you look at the source code of the rendered page, we can see the password for the root dn. Users are advised to upgrade. There is no known workaround for this issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/24xxx/CVE-2022-24867.json
- https://github.com/glpi-project/glpi/security/advisories/GHSA-4r49-52q9-5fgr
- https://nvd.nist.gov/vuln/detail/CVE-2022-24867
- https://github.com/glpi-project/glpi/commit/26f0a20810db11641afdcf671bac7a309acbb94e
