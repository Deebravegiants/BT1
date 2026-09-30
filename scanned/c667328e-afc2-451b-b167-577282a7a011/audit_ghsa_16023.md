# [H] Decidim-Awesome has SQL injection in AdminAccountability

## Summary
Severity: High
Advisory: GHSA-cxwf-qc32-375f
CVE: CVE-2024-43415
CWE: CWE-89
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:L (CVSS_V3)
Published: 2024-11-12
Source: https://github.com/advisories/GHSA-cxwf-qc32-375f
Type: github-advisory

## Affected
- RubyGems: `decidim-decidim_awesome` — affected >=0.9.1 <0.10.3
- RubyGems: `decidim-decidim_awesome` — affected >=0.11.0 <0.11.2

## Details
## Vulnerability type: 
CWE-89: Improper Neutralization of Special Elements used in an SQL Command ('SQL Injection')
## Vendor: 
Decidim International Community Environment

### Has vendor conﬁrmed: 
Yes

### Attack type:
Remote

### Impact:
Code Execution
Escalation of Privileges
Information Disclosure

### Aﬀected component:
A raw sql-statement that uses an interpolated variable exists in the admin_role_actions method of the
`papertrail/version-model(app/models/decidim/decidim_awesome/paper_trail_version.rb`).

### Attack vector:

An attacker with admin permissions could manipulate database queries in order to read out the database,
read ﬁles from the ﬁlesystem, write ﬁles from the ﬁlesystem. In the worst case, this could lead to remote code
execution on the server.
Description of the vulnerability for use in the CVE [ℹ] (https://cveproject.github.io/docs/content/key-details-
phrasing.pdf) : An improper neutralization of special elements used in an SQL command in the `papertrail/version-
model` of the decidim_awesome-module <= v0.11.1 (> 0.9.0) allows an authenticated admin user to manipulate sql queries
to disclose information, read and write files or execute commands.

### Discoverer Credits:
Wolfgang Hotwagner

### References:
https://pentest.ait.ac.at/security-advisory/decidim-awesome-sql-injection-in-adminaccountability/
https://portswigger.net/web-security/sql-injection

## References
- https://github.com/decidim-ice/decidim-module-decidim_awesome/security/advisories/GHSA-cxwf-qc32-375f
- https://nvd.nist.gov/vuln/detail/CVE-2024-43415
- https://github.com/decidim-ice/decidim-module-decidim_awesome/commit/84374037d34a3ac80dc18406834169c65869f11b
- https://github.com/decidim-ice/decidim-module-decidim_awesome
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/decidim-decidim_awesome/CVE-2024-43415.yml
- https://pentest.ait.ac.at/security-advisory/decidim-awesome-sql-injection-in-adminaccountability
