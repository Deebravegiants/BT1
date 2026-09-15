# [M] CVE-2021-21354

## Summary
Severity: Medium
Advisory: CVE-2021-21354
Aliases: GHSA-jhgx-wmq8-jc24
CVSS: 6.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N)
Published: 2021-03-08
Source: https://osv.dev/vulnerability/CVE-2021-21354
Type: osv

## Details
Pollbot is open source software which "frees its human masters from the toilsome task of polling for the state of things during the Firefox release process." In Pollbot before version 1.4.4 there is an open redirection vulnerability in the path of "https://pollbot.services.mozilla.com/". An attacker can redirect anyone to malicious sites. To Reproduce type in this URL: "https://pollbot.services.mozilla.com//evil.com/". Affected versions will redirect to that website when you inject a payload like "//evil.com/". This is fixed in version 1.4.4.

## References
- https://cheatsheetseries.owasp.org/cheatsheets/Unvalidated_Redirects_and_Forwards_Cheat_Sheet.html
- https://github.com/mozilla/PollBot/releases/tag/v1.4.4
- https://bugzilla.mozilla.org/show_bug.cgi?id=1694684
- https://github.com/mozilla/PollBot/commit/6db74a4fcbff258c7cdf51a6ff0724fc10c485e5
- https://github.com/mozilla/PollBot/pull/333
- https://github.com/mozilla/PollBot/security/advisories/GHSA-jhgx-wmq8-jc24
