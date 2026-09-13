# [M] Mailpit: SMTP command parser buffers unbounded command lines before syntax rejection

## Summary
Severity: Medium
Advisory: CVE-2026-67445
Aliases: GHSA-w878-pj84-3j5v, GO-2026-6363
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2026-08-20
Source: https://osv.dev/vulnerability/CVE-2026-67445
Type: osv

## Details
Mailpit is an email testing tool and API for developers. Prior to 1.30.4, Mailpit reads SMTP commands through internal/smtpd/smtpd.go session.readLine() using bufio.Reader.ReadString before session.parseLine() parses the verb or the RFC 5321 512-octet command-line limit is enforced. An unauthenticated remote SMTP client can send an oversized single command line that is fully allocated before syntax rejection or timeout, and the normal MaxMessageSize and DATA limits do not apply to this pre-DATA path. The same command reader is used by handleAuthLogin(), handleAuthPlain(), and handleAuthCramMD5() continuation lines, so concurrent oversized inputs can create memory pressure and reduce service availability. This issue is fixed in version 1.30.4.

## References
- https://github.com/axllent/mailpit/releases/tag/v1.30.4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/67xxx/CVE-2026-67445.json
- https://github.com/axllent/mailpit/security/advisories/GHSA-w878-pj84-3j5v
- https://nvd.nist.gov/vuln/detail/CVE-2026-67445
- https://github.com/axllent/mailpit/commit/993bed95b3c74d95231af93bd0e0d4c3d5b4db4d
