# [M] pretalx mail templates vulnerable to email injection via unescaped user-controlled placeholders

## Summary
Severity: Medium
Advisory: GHSA-jm8c-9f3j-4378
CVE: CVE-2026-41426
CWE: CWE-116, CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-04-18
Source: https://github.com/advisories/GHSA-jm8c-9f3j-4378
Type: github-advisory

## Affected
- PyPI: `pretalx` — affected >=0 <2026.1.0

## Details
An unauthenticated attacker can send arbitrary HTML-rendered emails from a pretalx instance's configured sender address by embedding malformed HTML or markdown link syntax in a user-controlled template placeholder such as the account display name. The most direct vector is the password-reset flow: the attacker registers an account with a malicious name, enters the victim's email address, and triggers a password reset. The resulting email is delivered from the event's legitimate sender address and passes SPF/DKIM/DMARC validation, making it a ready-made phishing vector.

The same class of bug affects every mail template that interpolates a user-controlled placeholder (speaker name, proposal title, biography, question answers, etc.), including organiser-triggered emails such as acceptance/rejection notifications.

### Credits

Thanks go to Mark Fijneman for finding and reporting a subset of this issue, which alerted us to the wider vulnerability.

## References
- https://github.com/pretalx/pretalx/security/advisories/GHSA-jm8c-9f3j-4378
- https://nvd.nist.gov/vuln/detail/CVE-2026-41426
- https://github.com/pretalx/pretalx
- https://github.com/pypa/advisory-database/tree/main/vulns/pretalx/PYSEC-2026-109.yaml
