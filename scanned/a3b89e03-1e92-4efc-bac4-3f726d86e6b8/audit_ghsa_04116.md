# [H] Path Traversal in Action View

## Summary
Severity: High
Advisory: GHSA-86g5-2wh3-gc9j
CVE: CVE-2019-5418
CWE: CWE-22
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N/E:H (CVSS_V3)
Published: 2019-03-13
Source: https://github.com/advisories/GHSA-86g5-2wh3-gc9j
Type: github-advisory

## Affected
- RubyGems: `actionview` — affected >=5.2.0 <5.2.2.1
- RubyGems: `actionview` — affected >=4.0.0 <4.2.11.1
- RubyGems: `actionview` — affected >=5.1.0 <5.1.6.2
- RubyGems: `actionview` — affected >=5.0.0 <5.0.7.2

## Details
# File Content Disclosure in Action View

Impact 
------ 
There is a possible file content disclosure vulnerability in Action View.  Specially crafted accept headers in combination with calls to `render file:`  can cause arbitrary files on the target server to be rendered, disclosing the  file contents. 

The impact is limited to calls to `render` which render file contents without  a specified accept format.  Impacted code in a controller looks something like this: 

``` ruby
class UserController < ApplicationController 
  def index 
    render file: "#{Rails.root}/some/file" 
  end 
end 
``` 

Rendering templates as opposed to files is not impacted by this vulnerability. 

All users running an affected release should either upgrade or use one of the workarounds immediately. 

Releases 
-------- 
The 6.0.0.beta3, 5.2.2.1, 5.1.6.2, 5.0.7.2, and 4.2.11.1 releases are available at the normal locations. 

Workarounds 
----------- 
This vulnerability can be mitigated by specifying a format for file rendering, like this: 

``` ruby
class UserController < ApplicationController 
  def index 
    render file: "#{Rails.root}/some/file", formats: [:html] 
  end 
end 
``` 

In summary, impacted calls to `render` look like this: 

``` 
render file: "#{Rails.root}/some/file" 
``` 

The vulnerability can be mitigated by changing to this: 

``` 
render file: "#{Rails.root}/some/file", formats: [:html] 
``` 

Other calls to `render` are not impacted. 

Alternatively, the following monkey patch can be applied in an initializer: 

``` ruby
$ cat config/initializers/formats_filter.rb 
# frozen_string_literal: true 

ActionDispatch::Request.prepend(Module.new do 
  def formats 
    super().select do |format| 
      format.symbol || format.ref == "*/*" 
    end 
  end 
end) 
``` 

Credits 
------- 
Thanks to John Hawthorn <john@hawthorn.email> of GitHub

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-5418
- https://access.redhat.com/errata/RHSA-2019:0796
- https://access.redhat.com/errata/RHSA-2019:1147
- https://access.redhat.com/errata/RHSA-2019:1149
- https://access.redhat.com/errata/RHSA-2019:1289
- https://groups.google.com/forum/#!topic/rubyonrails-security/pFRKI96Sm8Q
- https://groups.google.com/forum/#!topic/rubyonrails-security/zRNVOUhKHrg
- https://groups.google.com/forum/#%21topic/rubyonrails-security/pFRKI96Sm8Q
- https://lists.debian.org/debian-lts-announce/2019/03/msg00042.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/Y43636TH4D6T46IC6N2RQVJTRFJAAYGA
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/Y43636TH4D6T46IC6N2RQVJTRFJAAYGA
- https://web.archive.org/web/20190313201629/https://weblog.rubyonrails.org/2019/3/13/Rails-4-2-5-1-5-1-6-2-have-been-released
- https://weblog.rubyonrails.org/2019/3/13/Rails-4-2-5-1-5-1-6-2-have-been-released
- https://www.cisa.gov/known-exploited-vulnerabilities-catalog?field_cve=CVE-2019-5418
- https://www.exploit-db.com/exploits/46585
- http://lists.opensuse.org/opensuse-security-announce/2019-05/msg00011.html
- http://packetstormsecurity.com/files/152178/Rails-5.2.1-Arbitrary-File-Content-Disclosure.html
- http://www.openwall.com/lists/oss-security/2019/03/22/1
