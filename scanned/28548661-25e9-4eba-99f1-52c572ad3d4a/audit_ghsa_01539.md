# [M] CSRF Vulnerability in rails-ujs

## Summary
Severity: Medium
Advisory: GHSA-xq5j-gw7f-jgj8
CVE: CVE-2020-8167
CWE: CWE-352
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2020-07-07
Source: https://github.com/advisories/GHSA-xq5j-gw7f-jgj8
Type: github-advisory

## Affected
- RubyGems: `actionview` — affected >=5.0.0 <5.2.4.3
- RubyGems: `actionview` — affected >=6.0.0 <6.0.3.1

## Details
There is a vulnerability in rails-ujs that allows attackers to send CSRF tokens to wrong domains.

Versions Affected:  rails <= 6.0.3
Not affected:       Applications which don't use rails-ujs.
Fixed Versions:     rails >= 5.2.4.3, rails >= 6.0.3.1

Impact
------

This is a regression of CVE-2015-1840.

In the scenario where an attacker might be able to control the href attribute of an anchor tag or the action attribute of a form tag that will trigger a POST action, the attacker can set the href or action to a cross-origin URL, and the CSRF token will be sent.

Workarounds
-----------

To work around this problem, change code that allows users to control the href attribute of an anchor tag or the action attribute of a form tag to filter the user parameters.

For example, code like this:

    link_to params

to code like this:

    link_to filtered_params

    def filtered_params
      # Filter just the parameters that you trust
    end

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-8167
- https://hackerone.com/reports/189878
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/actionview/CVE-2020-8167.yml
- https://groups.google.com/forum/#!topic/rubyonrails-security/x9DixQDG9a0
- https://groups.google.com/g/rubyonrails-security/c/x9DixQDG9a0
- https://www.debian.org/security/2020/dsa-4766
