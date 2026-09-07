# [M] will_paginate Cross-site Scripting vulnerability

## Summary
Severity: Medium
Advisory: GHSA-8r6h-7x9g-xmw9
CVE: CVE-2013-6459
CWE: CWE-79
Ecosystem: RubyGems
Published: 2017-10-24
Source: https://github.com/advisories/GHSA-8r6h-7x9g-xmw9
Type: github-advisory

## Affected
- RubyGems: `will_paginate` — affected >=0 <3.0.5

## Details
Cross-site scripting (XSS) vulnerability in the will_paginate gem before 3.0.5 for Ruby allows remote attackers to inject arbitrary web script or HTML via vectors involving generated pagination links.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-6459
- https://access.redhat.com/errata/RHSA-2018:0336
- https://github.com/mislav/will_paginate
- https://github.com/mislav/will_paginate/releases/tag/v3.0.5
- https://web.archive.org/web/20150709163604/http://www.securityfocus.com/bid/64509
