# [C] md2pdf allows context-dependent attackers to execute arbitrary commands via shell metacharacters in a filename

## Summary
Severity: Critical
Advisory: GHSA-99ch-8mvp-g7m5
CVE: CVE-2013-1948
Ecosystem: RubyGems
Published: 2017-10-24
Source: https://github.com/advisories/GHSA-99ch-8mvp-g7m5
Type: github-advisory

## Affected
- RubyGems: `md2pdf` — affected >=0

## Details
`converter.rb` in the md2pdf gem 0.0.1 for Ruby allows context-dependent attackers to execute arbitrary commands via shell metacharacters in a filename.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-1948
- https://exchange.xforce.ibmcloud.com/vulnerabilities/83416
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/md2pdf/CVE-2013-1948.yml
- https://github.com/rwestgeest/md2pdf
- https://web.archive.org/web/20130503194109/http://www.securityfocus.com/bid/59061
- http://vapid.dhs.org/advisories/md2pdf-remote-exec.html
