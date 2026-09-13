# [M] actionview contains Path Traversal vulnerability

## Summary
Severity: Medium
Advisory: GHSA-vx9j-46rh-fqr8
CVE: CVE-2016-2097
CWE: CWE-22
Ecosystem: RubyGems
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2017-10-24
Source: https://github.com/advisories/GHSA-vx9j-46rh-fqr8
Type: github-advisory

## Affected
- RubyGems: `actionview` — affected >=3.0.0 <3.2.22.2
- RubyGems: `actionview` — affected >=4.0.0 <4.1.14.2
- RubyGems: `actionpack` — affected >=3.0.0 <3.2.22.2
- RubyGems: `actionpack` — affected >=4.0.0 <4.1.14.2

## Details
There is a possible directory traversal and information leak vulnerability in Action View. This was meant to be fixed on CVE-2016-0752. However the 3.2 patch was not covering all possible scenarios. This vulnerability has been assigned the CVE identifier CVE-2016-2097.

Versions Affected:  3.2.x, 4.0.x, 4.1.x
Not affected:       4.2+
Fixed Versions:     3.2.22.2, 4.1.14.2

Impact
------
Applications that pass unverified user input to the `render` method in a controller may be vulnerable to an information leak vulnerability.

Impacted code will look something like this:

```ruby
def index
  render params[:id]
end
```

Carefully crafted requests can cause the above code to render files from unexpected places like outside the application's view directory, and can possibly escalate this to a remote code execution attack.

All users running an affected release should either upgrade or use one of the workarounds immediately.

Releases
--------
The FIXED releases are available at the normal locations.

Workarounds
-----------
A workaround to this issue is to not pass arbitrary user input to the `render` method. Instead, verify that data before passing it to the `render` method.

For example, change this:

```ruby
def index
  render params[:id]
end
```

To this:

```ruby
def index
  render verify_template(params[:id])
end

private
def verify_template(name)
  # add verification logic particular to your application here
end
```

Patches
-------
To aid users who aren't able to upgrade immediately we have provided patches for it. It is in git-am format and consist of a single changeset.

* 3-2-render_data_leak_2.patch - Patch for 3.2 series
* 4-1-render_data_leak_2.patch - Patch for 4.1 series

Credits
-------
Thanks to both Jyoti Singh and Tobias Kraze from makandra for reporting this and working with us in the patch!

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-2097
- https://github.com/rails/rails/commit/8a1d3ea617ffb0c8ae8467fa439bf63a3bfc4324
- https://github.com/rails/rails
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/actionpack/CVE-2016-2097.yml
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/actionview/CVE-2016-2097.yml
- https://groups.google.com/forum/#!topic/rubyonrails-security/ddY6HgqB2z4
- https://web.archive.org/web/20160322002234/http://www.securitytracker.com/id/1035122
- https://web.archive.org/web/20200228015320/http://www.securityfocus.com/bid/83726
- https://web.archive.org/web/20201221115217/https://groups.google.com/forum/message/raw?msg=rubyonrails-security/ddY6HgqB2z4/we0RasMZIAAJ
- http://lists.opensuse.org/opensuse-security-announce/2016-03/msg00080.html
- http://lists.opensuse.org/opensuse-security-announce/2016-03/msg00083.html
- http://lists.opensuse.org/opensuse-security-announce/2016-04/msg00006.html
- http://weblog.rubyonrails.org/2016/2/29/Rails-4-2-5-2-4-1-14-2-3-2-22-2-have-been-released
- http://www.debian.org/security/2016/dsa-3509
