# [C] TeamPass vulnerable to SQL Injection

## Summary
Severity: Critical
Advisory: GHSA-r64j-5w3w-fp49
CVE: CVE-2015-7564
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-r64j-5w3w-fp49
Type: github-advisory

## Affected
- Packagist: `nilsteampassnet/teampass` — affected >=0 <2.1.25

## Details
Multiple SQL injection vulnerabilities in TeamPass 2.1.24 and earlier allow remote attackers to execute arbitrary SQL commands via the (1) id parameter in an action_on_quick_icon action to item.query.php or the (2) order or (3) direction parameter in an (a) connections_logs, (b) errors_logs or (c) access_logs action to view.query.php.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-7564
- https://github.com/nilsteampassnet/TeamPass/pull/1140
- https://github.com/nilsteampassnet/TeamPass
- https://www.exploit-db.com/exploits/39559
