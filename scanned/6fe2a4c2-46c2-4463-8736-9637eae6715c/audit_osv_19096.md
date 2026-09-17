# [C] CVE-2020-7247

## Summary
Severity: Critical
Advisory: CVE-2020-7247
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-01-29
Source: https://osv.dev/vulnerability/CVE-2020-7247
Type: osv

## Details
smtp_mailaddr in smtp_session.c in OpenSMTPD 6.6, as used in OpenBSD 6.6 and other products, allows remote attackers to execute arbitrary commands as root via a crafted SMTP session, as demonstrated by shell metacharacters in a MAIL FROM field. This affects the "uncommented" default configuration. The issue exists because of an incorrect return value upon failure of input validation.

## References
- https://www.cisa.gov/known-exploited-vulnerabilities-catalog?field_cve=CVE-2020-7247
- http://packetstormsecurity.com/files/162093/OpenBSD-OpenSMTPD-6.6-Remote-Code-Execution.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/OPH4QU4DNVHA7ACFXMYFCEP5PSXXPN4E/
- https://seclists.org/bugtraq/2020/Jan/51
- https://usn.ubuntu.com/4268-1/
- https://www.debian.org/security/2020/dsa-4611
- https://www.kb.cert.org/vuls/id/390745
- https://github.com/openbsd/src/commit/9dcfda045474d8903224d175907bfc29761dcb45
- https://www.openbsd.org/security.html
- http://packetstormsecurity.com/files/156137/OpenBSD-OpenSMTPD-Privilege-Escalation-Code-Execution.html
- http://packetstormsecurity.com/files/156145/OpenSMTPD-6.6.2-Remote-Code-Execution.html
- http://packetstormsecurity.com/files/156249/OpenSMTPD-MAIL-FROM-Remote-Code-Execution.html
- http://packetstormsecurity.com/files/156295/OpenSMTPD-6.6.1-Local-Privilege-Escalation.html
- http://seclists.org/fulldisclosure/2020/Jan/49
- http://www.openwall.com/lists/oss-security/2020/01/28/3
