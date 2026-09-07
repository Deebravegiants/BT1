# [M] ActionText ContentAttachment can Contain Unsanitized HTML

## Summary
Severity: Medium
Advisory: GHSA-prjp-h48f-jgf6
CVE: CVE-2024-32464
CWE: CWE-79
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2024-06-04
Source: https://github.com/advisories/GHSA-prjp-h48f-jgf6
Type: github-advisory

## Affected
- RubyGems: `actiontext` — affected >=7.1.0 <7.1.3.4
- RubyGems: `actiontext` — affected >=7.2.0.beta1 <7.2.0.beta2

## Details
Instances of ActionText::Attachable::ContentAttachment included within a rich_text_area tag could potentially contain unsanitized HTML.

This has been assigned the CVE identifier CVE-2024-32464.


Versions Affected:  >= 7.1.0
Not affected:       < 7.1.0
Fixed Versions:     7.1.3.4

Impact
------
This could lead to a potential cross site scripting issue within the Trix editor.

Releases
--------
The fixed releases are available at the normal locations.

Workarounds
-----------
N/A

Patches
-------
To aid users who aren't able to upgrade immediately we have provided patches for the supported release series in accordance with our [maintenance policy](https://guides.rubyonrails.org/maintenance_policy.html#security-issues) regarding security issues. They are in git-am format and consist of a single changeset.

* action_text_content_attachment_xss_7_1_stable.patch - Patch for 7.1 series



Credits
-------

Thank you [ooooooo_q](https://hackerone.com/ooooooo_q) for reporting this!

## References
- https://github.com/rails/rails/security/advisories/GHSA-prjp-h48f-jgf6
- https://nvd.nist.gov/vuln/detail/CVE-2024-32464
- https://github.com/rails/rails/commit/e215bf3360e6dfe1497c1503a495e384ed6b0995
- https://github.com/rails/rails
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/actiontext/CVE-2024-32464.yml
