# [M] CVE-2025-1015

## Summary
Severity: Medium
Advisory: CVE-2025-1015
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:N)
Published: 2025-02-04
Source: https://osv.dev/vulnerability/CVE-2025-1015
Type: osv

## Details
The Thunderbird Address Book URI fields contained unsanitized links. This could be used by an attacker to create and export an address book containing a malicious payload in a field. For example, in the “Other” field of the Instant Messaging section. If another user imported the address book, clicking on the link could result in opening a web page inside Thunderbird, and that page could execute (unprivileged) JavaScript. This vulnerability affects Thunderbird < 128.7 and Thunderbird < 135.

## References
- https://www.mozilla.org/security/advisories/mfsa2025-10/
- https://www.mozilla.org/security/advisories/mfsa2025-11/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1939458
