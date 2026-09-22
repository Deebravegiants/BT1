# [M] CVE-2023-0616

## Summary
Severity: Medium
Advisory: CVE-2023-0616
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2023-06-02
Source: https://osv.dev/vulnerability/CVE-2023-0616
Type: osv

## Details
If a MIME email combines OpenPGP and OpenPGP MIME data in a certain way Thunderbird repeatedly attempts to process and display the message, which could cause Thunderbird's user interface to lock up and no longer respond to the user's actions. An attacker could send a crafted message with this structure to attempt a DoS attack. This vulnerability affects Thunderbird < 102.8.

## References
- https://www.mozilla.org/security/advisories/mfsa2023-07/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1806507
