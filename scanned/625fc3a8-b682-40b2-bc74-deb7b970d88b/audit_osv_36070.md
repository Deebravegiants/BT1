# [H] Rsyslog: a configuration-dependent issue in rsyslog's optional imptcp input module can allow an unauthenticated remote peer to crash rsyslogd

## Summary
Severity: High
Advisory: CVE-2026-19654
Aliases: GHSA-cj5r-wh2m-7w29
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-12
Source: https://osv.dev/vulnerability/CVE-2026-19654
Type: osv

## Details
A unauthenticated remote peer may lead rsyslogd to crash due to a flaw in the optional imptcp module. A crafted input sequence during oversize-frame recovery can cause an invalid internal message length and terminate rsyslogd. No confidentiality or integrity impact, privilege escalation, or code execution has been identified. imtcp and the default imptcp framing modes are not affected.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://access.redhat.com/errata/RHSA-2026:66405
- https://access.redhat.com/security/cve/CVE-2026-19654
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/19xxx/CVE-2026-19654.json
- https://github.com/rsyslog/rsyslog/security/advisories/GHSA-cj5r-wh2m-7w29
- https://nvd.nist.gov/vuln/detail/CVE-2026-19654
- https://bugzilla.redhat.com/show_bug.cgi?id=2502868
