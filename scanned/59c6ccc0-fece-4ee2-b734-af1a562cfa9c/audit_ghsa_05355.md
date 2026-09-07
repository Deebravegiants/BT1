# [M] katello: missing repository authorization in content_uploads exposes cross-product content existence

## Summary
Severity: Medium
Advisory: GHSA-c43c-rf7g-5xpg
CVE: CVE-2026-12515
CWE: CWE-862
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-06-17
Source: https://github.com/advisories/GHSA-c43c-rf7g-5xpg
Type: github-advisory

## Affected
- RubyGems: `katello` — affected >=0 <4.21.0.rc1

## Details
A flaw was found in Katello's of Red Hat Satellite. A content upload functionality where insufficient authorization checks in the ContentUploadsController allowed users with the edit_products permission to query content information for repositories outside the products they were authorized to manage. An authenticated attacker could exploit this issue to determine whether specific content exists within repositories that should otherwise be inaccessible. This issue does not allow unauthorized modification, import, or publication of content.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-12515
- https://github.com/Katello/katello/pull/11712
- https://access.redhat.com/errata/RHSA-2026:50221
- https://access.redhat.com/errata/RHSA-2026:50222
- https://access.redhat.com/errata/RHSA-2026:50223
- https://access.redhat.com/errata/RHSA-2026:50263
- https://access.redhat.com/security/cve/CVE-2026-12515
- https://bugzilla.redhat.com/show_bug.cgi?id=2489812
- https://github.com/Katello/katello
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/katello/CVE-2026-12515.yml
