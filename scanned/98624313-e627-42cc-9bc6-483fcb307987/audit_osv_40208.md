# [M] WebDyne::Session versions before 3.003_704 for Perl generate the session id insecurely

## Summary
Severity: Medium
Advisory: CVE-2026-5084
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2026-05-11
Source: https://osv.dev/vulnerability/CVE-2026-5084
Type: osv

## Details
WebDyne::Session versions before 3.003_704 for Perl generate the session id insecurely.

The session handler generates the session id from an MD5 hash seeded with a call to the built-in rand() function. The rand function is passed a maximum value based on the process id, the epoch time and the reference address of the object, but this information will have no effect on the overall quality of the seed of the message digest.

The rand function is seeded by 32-bits and is predictable. It is considered unsuitable for cryptographic purposes.

Predictable session ids could allow an attacker to gain access to systems.

Note that WebDyne::Session versions 1.042 and earlier appear to be in separate distributions from WebDyne.

## References
- http://www.openwall.com/lists/oss-security/2026/05/11/3
- https://cpan.org/modules
- https://metacpan.org/release/ASPEER/WebDyne-2.075/source/lib/WebDyne/Session.pm#L120
- https://webdyne.org
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/5xxx/CVE-2026-5084.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-5084
- https://github.com/aspeer/WebDyne/commit/7a3f949dc24e62a276eb0db629db64aca356e954.patch
- https://github.com/aspeer/WebDyne
- https://security.metacpan.org/docs/guides/random-data-for-security.html
