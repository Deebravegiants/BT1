# [M] CVE-2024-11696

## Summary
Severity: Medium
Advisory: CVE-2024-11696
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:N)
Published: 2024-11-26
Source: https://osv.dev/vulnerability/CVE-2024-11696
Type: osv

## Details
The application failed to account for exceptions thrown by the `loadManifestFromFile` method during add-on signature verification. This flaw, triggered by an invalid or unsupported extension manifest, could have caused runtime errors that disrupted the signature validation process. As a result, the enforcement of signature validation for unrelated add-ons may have been bypassed.  Signature validation in this context is used to ensure that third-party applications on the user's computer have not tampered with the user's extensions, limiting the impact of this issue. This vulnerability affects Firefox < 133, Firefox ESR < 128.5, Thunderbird < 133, and Thunderbird < 128.5.

## References
- https://lists.debian.org/debian-lts-announce/2024/11/msg00029.html
- https://www.mozilla.org/security/advisories/mfsa2024-64/
- https://www.mozilla.org/security/advisories/mfsa2024-67/
- https://www.mozilla.org/security/advisories/mfsa2024-68/
- https://www.mozilla.org/security/advisories/mfsa2024-63/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1929600
