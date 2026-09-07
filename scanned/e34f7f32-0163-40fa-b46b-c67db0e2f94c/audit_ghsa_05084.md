# [H] LimeSurvey has a SQL Injection issue

## Summary
Severity: High
Advisory: GHSA-pr6f-87hf-hx24
CVE: CVE-2026-50636
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-06-09
Source: https://github.com/advisories/GHSA-pr6f-87hf-hx24
Type: github-advisory

## Affected
- Packagist: `limesurvey/limesurvey` — affected >=0

## Details
The RemoteControl API methods invite_participants and remind_participants pass a caller-supplied token-ID array into TokenDynamic::findUninvited(), which concatenates the values directly into a tid IN ('...') SQL clause without parameterization or input validation. A remote, authenticated attacker holding the tokens/update permission on a survey can inject a crafted array element to perform SQL injection. Because LimeSurvey configures its PDO connection with emulated prepared statements (emulatePrepare = true) and does not disable MySQL multi-statements, the injection supports stacked queries: the attacker can append arbitrary additional statements (INSERT/UPDATE/DELETE/DROP/CREATE) after the original SELECT. This permits both arbitrary read of any data in the database, such as administrator bcrypt password hashes (lime_users), survey response PII, session records, and global settings, all recoverable via a SLEEP() time-based blind oracle, and arbitrary write/destruction of that data, including directly overwriting the administrator password hash for immediate account takeover or dropping/truncating tables. Reads and writes extend to any schema the application's database user can access. The RemoteControl interface (RPCInterface = json/xml) must be enabled, which is not the default.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-50636
- https://github.com/LimeSurvey/LimeSurvey/pull/5031
- https://github.com/LimeSurvey/LimeSurvey/commit/4f383aa0bbe711f0064b319edb19fba759c50a33
- https://github.com/LimeSurvey/LimeSurvey/commit/98cfee55df97f9c82a72cf352bb204d51e588f7e
- https://github.com/LimeSurvey/LimeSurvey
- https://www.limesurvey.org
- https://www.vulncheck.com/advisories/limesurvey-remotecontrol-invite-participants-remind-participants-sql-injection
