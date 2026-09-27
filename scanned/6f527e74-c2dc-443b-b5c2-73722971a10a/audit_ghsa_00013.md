# [M] Exposure of Sensitive Information to an Unauthorized Actor in activestorage

## Summary
Severity: Medium
Advisory: GHSA-7rr7-rcjw-56vj
CVE: CVE-2018-16477
CWE: CWE-200
Ecosystem: RubyGems
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2018-12-05
Source: https://github.com/advisories/GHSA-7rr7-rcjw-56vj
Type: github-advisory

## Affected
- RubyGems: `activestorage` — affected >=5.2.0 <5.2.1.1

## Details
A bypass vulnerability in Active Storage >= 5.2.0 for Google Cloud Storage and Disk services allow an attacker to modify the `content-disposition` and `content-type` parameters which can be used in with HTML files and have them executed inline. Additionally, if combined with other techniques such as cookie bombing and specially crafted AppCache manifests, an attacker can gain access to private signed URLs within a specific storage path.

Vulnerable apps are those using either GCS or the Disk service in production. Other storage services such as S3 or Azure aren't affected.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-16477
- https://github.com/advisories/GHSA-7rr7-rcjw-56vj
- https://groups.google.com/d/msg/rubyonrails-security/3KQRnXDIuLg/mByx5KkqBAAJ
- https://weblog.rubyonrails.org/2018/11/27/Rails-4-2-5-0-5-1-5-2-have-been-released
