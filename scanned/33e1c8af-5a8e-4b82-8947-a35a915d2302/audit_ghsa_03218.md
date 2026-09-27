# [H] Denial of Service in Action Dispatch

## Summary
Severity: High
Advisory: GHSA-g8ww-46x2-2p65
CVE: CVE-2021-22902
CWE: CWE-400
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-05-05
Source: https://github.com/advisories/GHSA-g8ww-46x2-2p65
Type: github-advisory

## Affected
- RubyGems: `actionpack` — affected >=6.0.0 <6.0.3.7
- RubyGems: `actionpack` — affected >=6.1.0 <6.1.3.2

## Details
Impact
------
There is a possible Denial of Service vulnerability in Action Dispatch. Carefully crafted Accept headers can cause the mime type parser in Action Dispatch to do catastrophic backtracking in the regular expression engine.

Releases
--------
The fixed releases are available at the normal locations.

Workarounds
-----------
The following monkey patch placed in an initializer can be used to work around the issue.

```ruby
module Mime
  class Type
    MIME_REGEXP = /\A(?:\*\/\*|#{MIME_NAME}\/(?:\*|#{MIME_NAME})(?>\s*#{MIME_PARAMETER}\s*)*)\z/
  end
end
```

Patches
-------
To aid users who aren't able to upgrade immediately we have provided patches for the two supported release series. They are in git-am format and consist of a single changeset.

* 6-0-Prevent-catastrophic-backtracking-during-mime-parsin.patch - Patch for 6.0 series
* 6-1-Prevent-catastrophic-backtracking-during-mime-parsin.patch - Patch for 6.1 series

Please note that only the 6.1.Z, 6.0.Z, and 5.2.Z series are supported at present. Users of earlier unsupported releases are advised to upgrade as soon as possible as we cannot guarantee the continued availability of security fixes for unsupported releases.

Credits
-------

Thanks to Security Curious <security...@pm.me> for reporting this!

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-22902
- https://hackerone.com/reports/1138654
- https://discuss.rubyonrails.org/t/cve-2021-22902-possible-denial-of-service-vulnerability-in-action-dispatch/77866
- https://github.com/rails/rails/releases/tag/v6.0.3.7
- https://github.com/rails/rails/releases/tag/v6.1.3.2
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/actionpack/CVE-2021-22902.yml
- https://groups.google.com/g/rubyonrails-security/c/_5ID_ld9u1c
