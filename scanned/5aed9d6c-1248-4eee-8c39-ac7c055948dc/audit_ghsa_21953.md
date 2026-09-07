# [M] open redirect in pollbot

## Summary
Severity: Medium
Advisory: GHSA-vg27-hr3v-3cqv
CVE: CVE-2022-0637
CWE: CWE-601
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-02-16
Source: https://github.com/advisories/GHSA-vg27-hr3v-3cqv
Type: github-advisory

## Affected
- PyPI: `pollbot` — affected >=0 <1.4.6

## Details
(From https://bugzilla.mozilla.org/show_bug.cgi?id=1753838)

Summary:
There was an open redirection vulnerability in the path of:

https://pollbot.services.mozilla.com/ and https://pollbot.stage.mozaws.net/

Description:
An attacker can redirect anyone to malicious sites.

Steps To Reproduce:
Type in this URL:

https://pollbot.services.mozilla.com/%0a/evil.com/

It redirects to that website

evil.com

evil.com was used as an example but this could be any website. Note, the /%0a/ and trailing / are required.

Supporting Material/References:
https://cheatsheetseries.owasp.org/cheatsheets/Unvalidated_Redirects_and_Forwards_Cheat_Sheet.html

Impact

Attackers can serve malicious websites that steal passwords or download ransomware to their victims machine due to a redirect and there are a heap of other attack vectors.

## References
- https://github.com/mozilla/PollBot/security/advisories/GHSA-vg27-hr3v-3cqv
- https://nvd.nist.gov/vuln/detail/CVE-2022-0637
- https://github.com/mozilla/PollBot/pull/360
- https://github.com/mozilla/PollBot/commit/e39d8bec2df582ba525bb2e2f33c3ebc584d7ff8
- https://bugzilla.mozilla.org/show_bug.cgi?id=1753838
- https://bugzilla.mozilla.org/show_bug.cgi?id=CVE-2022-0637
- https://github.com/mozilla/PollBot
