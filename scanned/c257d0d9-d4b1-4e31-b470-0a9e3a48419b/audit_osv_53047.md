# [H] CVE-2022-26387

## Summary
Severity: High
Advisory: CVE-2022-26387
CVSS: 7.5 (CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2022-12-22
Source: https://osv.dev/vulnerability/CVE-2022-26387
Type: osv

## Details
When installing an add-on, Firefox verified the signature before prompting the user; but while the user was confirming the prompt, the underlying add-on file could have been modified and Firefox would not have noticed. This vulnerability affects Firefox < 98, Firefox ESR < 91.7, and Thunderbird < 91.7.

## References
- https://www.mozilla.org/security/advisories/mfsa2022-10/
- https://www.mozilla.org/security/advisories/mfsa2022-11/
- https://www.mozilla.org/security/advisories/mfsa2022-12/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1752979
