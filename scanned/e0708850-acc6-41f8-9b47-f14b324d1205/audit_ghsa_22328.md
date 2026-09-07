# [M] Drupal Open Redirect

## Summary
Severity: Medium
Advisory: GHSA-wwrm-8947-4m6c
CVE: CVE-2012-1589
CWE: CWE-20, CWE-601
Ecosystem: Packagist
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-wwrm-8947-4m6c
Type: github-advisory

## Affected
- Packagist: `drupal/drupal` — affected >=7.0 <7.13

## Details
Open redirect vulnerability in the Form API in Drupal 7.x before 7.13 allows remote attackers to redirect users to arbitrary web sites and conduct phishing attacks via crafted parameters in a destination URL.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2012-1589
- https://web.archive.org/web/20120507035905/http://www.securityfocus.com/bid/53365
- https://web.archive.org/web/20150523060428/http://www.mandriva.com/en/support/security/advisories/advisory/MDVSA-2013:074/?name=MDVSA-2013:074
- http://drupal.org/node/1557938
- http://jvn.jp/en/jp/JVN45898075/index.html
- http://jvndb.jvn.jp/jvndb/JVNDB-2012-000045
