# [C] Katello uses hard coded credential

## Summary
Severity: Critical
Advisory: GHSA-5xv2-q475-rwrh
CVE: CVE-2012-3503
CWE: CWE-798
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-5xv2-q475-rwrh
Type: github-advisory

## Affected
- RubyGems: `katello` — affected >=0 <1.0.6
- RubyGems: `katello` — affected >=1.1.0 <1.1.7

## Details
The installation script in Katello 1.0 and earlier does not properly generate the `Application.config.secret_token` value, which causes each default installation to have the same secret token, and allows remote attackers to authenticate to the CloudForms System Engine web interface as an arbitrary user by creating a cookie using the default `secret_token`.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2012-3503
- https://github.com/Katello/katello/pull/499
- https://github.com/Katello/katello/commit/7c256fef9d75029d0ffff58ff1dcda915056d3a3
- https://github.com/Katello/katello
- https://github.com/advisories/GHSA-5xv2-q475-rwrh
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/katello/CVE-2012-3503.yml
- https://web.archive.org/web/20140806122239/http://secunia.com/advisories/50344
- https://web.archive.org/web/20200229120740/http://www.securityfocus.com/bid/55140
- http://rhn.redhat.com/errata/RHSA-2012-1186.html
- http://rhn.redhat.com/errata/RHSA-2012-1187.html
