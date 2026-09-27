# [H] CVE-2017-5448

## Summary
Severity: High
Advisory: CVE-2017-5448
CVSS: 8.6 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:H)
Published: 2018-06-11
Source: https://osv.dev/vulnerability/CVE-2017-5448
Type: osv

## Details
An out-of-bounds write in "ClearKeyDecryptor" while decrypting some Clearkey-encrypted media content. The "ClearKeyDecryptor" code runs within the Gecko Media Plugin (GMP) sandbox. If a second mechanism is found to escape the sandbox, this vulnerability allows for the writing of arbitrary data within memory, resulting in a potentially exploitable crash. This vulnerability affects Firefox ESR < 45.9, Firefox ESR < 52.1, and Firefox < 53.

## References
- http://www.securitytracker.com/id/1038320
- https://access.redhat.com/errata/RHSA-2017:1106
- https://www.debian.org/security/2017/dsa-3831
- https://www.mozilla.org/security/advisories/mfsa2017-11/
- http://www.securityfocus.com/bid/97940
- https://access.redhat.com/errata/RHSA-2017:1104
- https://www.mozilla.org/security/advisories/mfsa2017-10/
- https://www.mozilla.org/security/advisories/mfsa2017-12/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1346648
