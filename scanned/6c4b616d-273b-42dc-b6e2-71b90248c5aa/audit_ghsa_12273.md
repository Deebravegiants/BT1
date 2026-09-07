# [H] Webbynode Code Injection vulnerability

## Summary
Severity: High
Advisory: GHSA-p65m-qr5x-rrqq
CVE: CVE-2013-7086
CWE: CWE-94
Ecosystem: RubyGems
Published: 2017-10-24
Source: https://github.com/advisories/GHSA-p65m-qr5x-rrqq
Type: github-advisory

## Affected
- RubyGems: `webbynode` — affected >=0

## Details
The message function in `lib/webbynode/notify.rb` in the Webbynode gem 1.0.5.3 and earlier for Ruby allows context-dependent attackers to execute arbitrary commands via shell metacharacters in a growlnotify message.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-7086
- https://github.com/webbynode/webbynode/pull/85
- https://exchange.xforce.ibmcloud.com/vulnerabilities/89705
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/webbynode/CVE-2013-7086.yml
- https://github.com/webbynode/webbynode
- https://web.archive.org/web/20200229074410/http://www.securityfocus.com/bid/64289
- https://web.archive.org/web/20201208124343/http://www.vapid.dhs.org/advisories/webbynode-command-inj.html
- http://packetstormsecurity.com/files/124421
- http://seclists.org/oss-sec/2013/q4/493
- http://seclists.org/oss-sec/2013/q4/497
