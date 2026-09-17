# [M] CVE-2023-25728

## Summary
Severity: Medium
Advisory: CVE-2023-25728
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2023-06-02
Source: https://osv.dev/vulnerability/CVE-2023-25728
Type: osv

## Details
The <code>Content-Security-Policy-Report-Only</code> header could allow an attacker to leak a child iframe's unredacted URI when interaction with that iframe triggers a redirect. This vulnerability affects Firefox < 110, Thunderbird < 102.8, and Firefox ESR < 102.8.

## References
- https://www.mozilla.org/security/advisories/mfsa2023-05/
- https://www.mozilla.org/security/advisories/mfsa2023-06/
- https://www.mozilla.org/security/advisories/mfsa2023-07/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1790345
