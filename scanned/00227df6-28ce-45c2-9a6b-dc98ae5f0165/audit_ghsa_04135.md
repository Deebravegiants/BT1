# [H] Denial of Service Vulnerability in Action View

## Summary
Severity: High
Advisory: GHSA-m63j-wh5w-c252
CVE: CVE-2019-5419
CWE: CWE-400, CWE-770
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2019-03-13
Source: https://github.com/advisories/GHSA-m63j-wh5w-c252
Type: github-advisory

## Affected
- RubyGems: `actionview` — affected >=4.0.0 <4.2.11.1
- RubyGems: `actionview` — affected >=5.2.0 <5.2.2.1
- RubyGems: `actionview` — affected >=5.1.0 <5.1.6.2
- RubyGems: `actionview` — affected >=5.0.0 <5.0.7.2
- RubyGems: `actionview` — affected >=6.0.0.beta1 <6.0.0.beta3

## Details
# Denial of Service Vulnerability in Action View

Impact 
------ 
Specially crafted accept headers can cause the Action View template location code to consume 100% CPU, causing the server unable to process requests.  This impacts all Rails applications that render views. 

All users running an affected release should either upgrade or use one of the workarounds immediately. 

Releases 
-------- 
The 6.0.0.beta3, 5.2.2.1, 5.1.6.2, 5.0.7.2, and 4.2.11.1 releases are available at the normal locations. 

Workarounds 
----------- 
This vulnerability can be mitigated by wrapping `render` calls with `respond_to` blocks.  For example, the following example is vulnerable: 

``` ruby
class UserController < ApplicationController 
  def index 
    render "index" 
  end 
end 
``` 

But the following code is not vulnerable: 

```ruby 
class UserController < ApplicationController 
  def index 
    respond_to |format| 
      format.html { render "index" } 
    end 
  end 
end 
``` 

Implicit rendering is impacted, so this code is vulnerable: 

```ruby 
class UserController < ApplicationController 
  def index 
  end 
end 
``` 

But can be changed this this: 

```ruby 
class UserController < ApplicationController 
  def index 
    respond_to |format| 
      format.html { render "index" } 
    end 
  end 
end 
``` 

Alternatively to specifying the format, the following monkey patch can be applied in an initializer: 

``` 
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

Please note that only the 5.2.x, 5.1.x, 5.0.x, and 4.2.x series are supported at present. Users of earlier unsupported releases are advised to upgrade as soon as possible as we cannot guarantee the continued availability of security fixes for unsupported releases. 

Also note that the patches for this vulnerability are the same as CVE-2019-5418. 

Credits 
------- 
Thanks to John Hawthorn <john@hawthorn.email> of GitHub

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-5419
- https://github.com/rails/rails/pull/35708
- https://github.com/rails/rails/commit/f4c70c2222180b8d9d924f00af0c7fd632e26715
- https://access.redhat.com/errata/RHSA-2019:0796
- https://access.redhat.com/errata/RHSA-2019:1147
- https://access.redhat.com/errata/RHSA-2019:1149
- https://access.redhat.com/errata/RHSA-2019:1289
- https://github.com/rails/rails
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/actionview/CVE-2019-5419.yml
- https://groups.google.com/forum/#!topic/rubyonrails-security/GN7w9fFAQeI
- https://lists.debian.org/debian-lts-announce/2019/03/msg00042.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/Y43636TH4D6T46IC6N2RQVJTRFJAAYGA
- https://weblog.rubyonrails.org/2019/3/13/Rails-4-2-5-1-5-1-6-2-have-been-released
- http://lists.opensuse.org/opensuse-security-announce/2019-05/msg00011.html
- http://lists.opensuse.org/opensuse-security-announce/2019-06/msg00025.html
- http://lists.opensuse.org/opensuse-security-announce/2019-08/msg00001.html
- http://www.openwall.com/lists/oss-security/2019/03/22/1
