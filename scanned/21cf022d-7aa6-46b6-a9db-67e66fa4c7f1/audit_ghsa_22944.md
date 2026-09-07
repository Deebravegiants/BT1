# [C] Moodle Blind SSRF Risk in /badges/mybackpack.php

## Summary
Severity: Critical
Advisory: GHSA-jp4g-r8c9-3534
CVE: CVE-2019-3809
CWE: CWE-918
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-jp4g-r8c9-3534
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=3.1 <3.1.16

## Details
A flaw was found in Moodle versions 3.1 to 3.1.15 and earlier unsupported versions. The mybackpack functionality allowed setting the URL of badges, when it should be restricted to the Mozilla Open Badges backpack URL. This resulted in the possibility of blind SSRF via requests made by the page.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-3809
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2019-3809
- https://github.com/moodle/moodle
- https://moodle.org/mod/forum/discuss.php?d=381229#p1536766
- http://git.moodle.org/gw?p=moodle.git&a=search&h=HEAD&st=commit&s=MDL-64222
