# [H] CVE-2022-45414

## Summary
Severity: High
Advisory: CVE-2022-45414
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:N)
Published: 2022-12-22
Source: https://osv.dev/vulnerability/CVE-2022-45414
Type: osv

## Details
If a Thunderbird user quoted from an HTML email, for example by replying to the email, and the email contained either a VIDEO tag with the POSTER attribute or an OBJECT tag with a DATA attribute, a network request to the referenced remote URL was performed, regardless of a configuration to block remote content. An image loaded from the POSTER attribute was shown in the composer window. These issues could have given an attacker additional capabilities when targetting releases that did not yet have a fix for CVE-2022-3033 which was reported around three months ago. This vulnerability affects Thunderbird < 102.5.1.

## References
- https://www.mozilla.org/security/advisories/mfsa2022-50/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1788096
