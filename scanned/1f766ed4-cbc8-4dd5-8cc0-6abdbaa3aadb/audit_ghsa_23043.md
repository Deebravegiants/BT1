# [H] Drupal Access Control Bypass

## Summary
Severity: High
Advisory: GHSA-96vx-qf28-6f8m
CVE: CVE-2011-2687
CWE: CWE-284
Ecosystem: Packagist
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-96vx-qf28-6f8m
Type: github-advisory

## Affected
- Packagist: `drupal/core` — affected >=7.0 <7.3

## Details
Drupal 7.x before 7.3 allows remote attackers to bypass intended `node_access` restrictions via vectors related to a listing that shows nodes but lacks a JOIN clause for the node table.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2011-2687
- https://bugzilla.redhat.com/show_bug.cgi?id=717874
- https://web.archive.org/web/20110710024036/http://www.securityfocus.com/bid/48505
- http://bugs.debian.org/cgi-bin/bugreport.cgi?bug=633385
- http://drupal.org/node/1204582
- http://lists.fedoraproject.org/pipermail/package-announce/2011-July/062714.html
- http://lists.fedoraproject.org/pipermail/package-announce/2011-July/062722.html
- http://www.openwall.com/lists/oss-security/2011/07/11/2
- http://www.openwall.com/lists/oss-security/2011/07/12/16
