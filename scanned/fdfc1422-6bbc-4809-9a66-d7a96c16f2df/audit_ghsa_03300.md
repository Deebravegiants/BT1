# [M] Possible Open Redirect Vulnerability in Action Pack

## Summary
Severity: Medium
Advisory: GHSA-5hq2-xf89-9jxq
CVE: CVE-2021-22903
CWE: CWE-601
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2021-05-05
Source: https://github.com/advisories/GHSA-5hq2-xf89-9jxq
Type: github-advisory

## Affected
- RubyGems: `actionpack` — affected >=6.1.0.rc2 <6.1.3.2

## Details
There is a possible Open Redirect Vulnerability in Action Pack.

Versions Affected:  >= v6.1.0.rc2
Not affected:       < v6.1.0.rc2
Fixed Versions:     6.1.3.2

Impact
------
This is similar to CVE-2021-22881. Specially crafted Host headers in combination with certain "allowed host" formats can cause the Host Authorization middleware in Action Pack to redirect users to a malicious
website.

Since rails/rails@9bc7ea5, strings in config.hosts that do not have a leading dot are converted to regular expressions without proper escaping. This causes, for example, config.hosts << "sub.example.com" to permit a request with a Host header value of sub-example.com.


Releases
--------
The fixed releases are available at the normal locations.

Workarounds
-----------
The following monkey patch put in an initializer can be used as a workaround.

```ruby
class ActionDispatch::HostAuthorization::Permissions
  def sanitize_string(host)
    if host.start_with?(".")
      /\A(.+\.)?#{Regexp.escape(host[1..-1])}\z/i
    else
      /\A#{Regexp.escape host}\z/i
    end
  end
end
```

Patches
-------
To aid users who aren't able to upgrade immediately we have provided patches for the two supported release series. They are in git-am format and consist of a single changeset.

* 6-1-open-redirect.patch - Patch for 6.1 series

Please note that only the 6.1.Z, 6.0.Z, and 5.2.Z series are supported at present. Users of earlier unsupported releases are advised to upgrade as soon as possible as we cannot guarantee the continued availability of security fixes for unsupported releases.

Credits
-------

Thanks Jonathan Hefner (https://hackerone.com/jonathanhefner) for reporting this bug!

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-22903
- https://hackerone.com/reports/1148025
- https://discuss.rubyonrails.org/t/cve-2021-22903-possible-open-redirect-vulnerability-in-action-pack/77867
- https://github.com/rails/rails/releases/tag/v6.1.3.2
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/actionpack/CVE-2021-22903.yml
- https://groups.google.com/g/rubyonrails-security/c/8TxqXEtgSF0
