# [H] YesWiki has Persistent Blind XSS at "/?BazaR&vue=consulter"

## Summary
Severity: High
Advisory: GHSA-37fq-47qj-6j5j
CVE: CVE-2026-34598
CWE: CWE-79, CWE-87
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-04-01
Source: https://github.com/advisories/GHSA-37fq-47qj-6j5j
Type: github-advisory

## Affected
- Packagist: `yeswiki/yeswiki` — affected >=0 <4.6.0

## Details
### Summary
A stored and blind XSS vulnerability exists in the form title field. A malicious attacker can inject JavaScript without any authentication via a form title that is saved in the backend database. When any user visits that injected page, the JavaScript payload gets executed.

Type: Stored and Blind Cross-Site Scripting (XSS)
Affected Component: form title input field
Authentication Required: No (Unauthenticated attack possible)
Impact: Arbitrary JavaScript execution in victim’s browser


### Details
A Stored XSS vulnerability occurs when an application stores malicious user input (in this case, a script injected via the form title field) in its backend database and renders it later on a page viewed by other users without proper sanitization or encoding.

In this case, the attacker can inject JavaScript payloads in the title field of a form, which the application stores in the database. When any user, such as an admin or another visitor, views the page that displays this title, the malicious script executes in their browser context.

### PoC
- Visit `https://yeswiki.net/?BazaR&vue=formulaire` or `localhost/?BazaR&vue=formulaire` or 
 `https://ferme.yeswiki.net/[username]/?BazaR&vue=formulaire`
- Click on the `+` icon to add a record via the `Diary` form.
- Inject the payload like: `<script>alert(document.cookie)</script>` or `<script>alert(1)</script>` into `Name of the event` and `Description`
- Then save the record by clicking `To validate`
- The payload will be executed when anyone visits `/?BazaR&vue=consulter` also in the diary record 
`/?wiki=BazaR&vue=consulter&action=recherche&q=&id=2&facette=`

The payload is persistant.

## References
- https://github.com/YesWiki/yeswiki/security/advisories/GHSA-37fq-47qj-6j5j
- https://nvd.nist.gov/vuln/detail/CVE-2026-34598
- https://github.com/YesWiki/yeswiki
- https://github.com/YesWiki/yeswiki/releases/tag/v4.6.0
