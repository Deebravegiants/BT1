# [H] Action Pack contains Information Disclosure / Unintended Method Execution vulnerability

## Summary
Severity: High
Advisory: GHSA-hjg4-8q5f-x6fm
CVE: CVE-2021-22885
CWE: CWE-200, CWE-209
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2021-05-05
Source: https://github.com/advisories/GHSA-hjg4-8q5f-x6fm
Type: github-advisory

## Affected
- RubyGems: `actionpack` — affected >=6.0.0 <6.0.3.7
- RubyGems: `actionpack` — affected >=6.1.0 <6.1.3.2
- RubyGems: `actionpack` — affected >=5.2.5 <5.2.6
- RubyGems: `actionpack` — affected >=2.0.0 <5.2.4.6

## Details
Impact
------
There is a possible information disclosure / unintended method execution vulnerability in Action Pack when using the `redirect_to` or `polymorphic_url` helper with untrusted user input.

Vulnerable code will look like this.

```
redirect_to(params[:some_param])
```

All users running an affected release should either upgrade or use one of the workarounds immediately.

Releases
--------
The FIXED releases are available at the normal locations.

Workarounds
-----------
To work around this problem, it is recommended to use an allow list for valid parameters passed from the user.  For example,

```ruby
private def check(param)
  case param
  when "valid"
    param
  else
    "/"
  end
end

def index
  redirect_to(check(params[:some_param]))
end
```

Or force the user input to be cast to a string like this,

```ruby
def index
  redirect_to(params[:some_param].to_s)
end
```

Patches
-------
To aid users who aren't able to upgrade immediately we have provided patches for the two supported release series. They are in git-am format and consist of a single changeset.

* 5-2-information-disclosure.patch - Patch for 5.2 series
* 6-0-information-disclosure.patch - Patch for 6.0 series
* 6-1-information-disclosure.patch - Patch for 6.1 series

Please note that only the 5.2, 6.0, and 6.1 series are supported at present. Users of earlier unsupported releases are advised to upgrade as soon as possible as we cannot guarantee the continued availability of security fixes for unsupported releases.

Credits
-------

Thanks to Benoit Côté-Jodoin from Shopify for reporting this.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-22885
- https://hackerone.com/reports/1106652
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/actionpack/CVE-2021-22885.yml
- https://groups.google.com/g/rubyonrails-security/c/NiQl-48cXYI
- https://security.netapp.com/advisory/ntap-20210805-0009
