# [M] Rails vulnerable to Cross-site Scripting

## Summary
Severity: Medium
Advisory: GHSA-m46p-ggm5-5j83
CVE: CVE-2014-0081
CWE: CWE-79
Ecosystem: RubyGems
Published: 2017-10-24
Source: https://github.com/advisories/GHSA-m46p-ggm5-5j83
Type: github-advisory

## Affected
- RubyGems: `rails` — affected >=3.0.0 <3.2.17
- RubyGems: `rails` — affected >=4.0.0 <4.0.3
- RubyGems: `actionpack` — affected >=3.0.0 <3.2.17
- RubyGems: `actionpack` — affected >=4.0.0 <4.0.3

## Details
There is an XSS vulnerability in the `number_to_currency`, `number_to_percentage` and `number_to_human` helpers in Ruby on Rails. This vulnerability has been assigned the CVE identifier CVE-2014-0081.

Versions Affected:  All.
Fixed Versions:     4.1.0.beta2, 4.0.3, 3.2.17.

Impact
------
These helpers allows users to nicely format a numeric value. Some of the parameters to the helper (format, negative_format and units) are not escaped correctly. Applications which pass user controlled data as one of these parameters are vulnerable to an XSS attack.

All users passing user controlled data to these parameters of the number helpers should either upgrade or use one of the workarounds immediately.

Releases
--------
The 4.1.0.rc1, 4.0.3 and 3.2.17 releases are available at the normal locations.

Workarounds
-----------

The workaround for this issue is to escape the value passed to the parameter.
For example, replace code like this:

```ruby
<%= number_to_currency(1.02, format: params[:format]) %>
```

With code like this

```ruby
<%= number_to_currency(1.02, format: h(params[:format])) %>
```

Patches
-------
To aid users who aren't able to upgrade immediately we have provided patches for the two supported release series. They are in git-am format and consist of a single changeset.

* 4-1-beta-number_helpers_xss.patch - Patch for 4.1-beta series
* 4-0-number_helpers_xss.patch - Patch for 4.0 series
* 3-2-number_helpers_xss.patch - Patch for 3.2 series

Please note that only the 4.0.x and 3.2.x series are supported at present. Users of earlier unsupported releases are advised to upgrade as soon as possible as we cannot guarantee the continued availability of security fixes for unsupported releases.

Credits
-------

Thanks to Kevin Reintjes for reporting the issue to us.

-- 
Aaron Patterson
http://tenderlovemaking.com/

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-0081
- https://github.com/rails/rails/commit/08d0a11a3f62718d601d39e617c834759cf59bbb
- https://github.com/rails/rails
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/actionpack/CVE-2014-0081.yml
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/rails/CVE-2014-0081.yml
- https://web.archive.org/web/20140911141416/http://www.securitytracker.com/id/1029782
- https://web.archive.org/web/20170307202606/http://www.securityfocus.com/bid/65647
- https://web.archive.org/web/20201207045136/https://groups.google.com/forum/message/raw?msg=rubyonrails-security/tfp6gZCtzr4/j8LUHmu7fIEJ
- http://lists.opensuse.org/opensuse-updates/2014-02/msg00081.html
- http://openwall.com/lists/oss-security/2014/02/18/8
- http://rhn.redhat.com/errata/RHSA-2014-0215.html
- http://rhn.redhat.com/errata/RHSA-2014-0306.html
