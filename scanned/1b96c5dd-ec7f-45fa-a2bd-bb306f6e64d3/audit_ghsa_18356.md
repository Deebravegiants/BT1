# [H] go-mail has insufficient address encoding when passing mail addresses to the SMTP client

## Summary
Severity: High
Advisory: GHSA-wpwj-69cm-q9c5
CVE: CVE-2025-59937
CWE: CWE-88
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-09-29
Source: https://github.com/advisories/GHSA-wpwj-69cm-q9c5
Type: github-advisory

## Affected
- Go: `github.com/wneessen/go-mail` — affected >=0 <0.7.1

## Details
### Impact
Due to incorrect handling of the `mail.Address` values when a sender- or recipient address is passed to the corresponding `MAIL FROM` or `RCPT TO` commands of the SMTP client, this could lead to a possible wrong address routing or even to ESMTP parameter smuggling.

#### Vulnerability details
Instead of making use of the `String()` method of `mail.Address`, which takes care of proper escaping and quotation of mail address, we used the `Address` value of the `mail.Address` which is the raw value when passing it to our SMTP client.

This meant, if a mail address like this was set: `"toni.tester@example.com> ORCPT=admin@admin.com"@example.com` for a sender or recipient, instead of the correctly quoted/escaped address, the SMTP client would get the raw value passed which would translate into something like this being passed to the SMTP server: `RCPT TO:<toni.tester@example.com> ORCPT=admin@admin.com@example.com>`. 

Since ORCTP is a valid command for the SMTP server, the mail would be routed to the wrong address. Additionally, other SMTP commands could potientially be smuggled in using this method causing unexpected behaviour.

#### Exploitation requirements
For successful exploitation of this vulnerability it is required that the user's code is allowing for arbitrary mail address input (i. e. through a web form or similar). If only static mail addresses are used (i. e. in a config file) and the mail addresses in use do not consist of quoted local parts, this should not affect your code.

### Patches
The vulnerability has been fixed with PR #496 and the fix has been shipped with the go-mail v0.7.1 release.

Issue #495 holds the full report and discussion.

## References
- https://github.com/wneessen/go-mail/security/advisories/GHSA-wpwj-69cm-q9c5
- https://nvd.nist.gov/vuln/detail/CVE-2025-59937
- https://github.com/wneessen/go-mail/issues/495
- https://github.com/wneessen/go-mail/pull/496
- https://github.com/wneessen/go-mail/commit/42e92cfe027be04aff72921adb0f72f11d517479
- https://github.com/wneessen/go-mail
- https://pkg.go.dev/vuln/GO-2025-3988
