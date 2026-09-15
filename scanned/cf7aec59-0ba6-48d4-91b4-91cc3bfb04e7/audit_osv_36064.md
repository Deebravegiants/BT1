# [H] Freeipa: ipa: freeipa: trust-fetch-domains uses trust-read aci to gate a privileged ad trust refresh, allowing unauthorized ldap writes

## Summary
Severity: High
Advisory: CVE-2026-19550
CVSS: 8.2 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:H/I:H/A:N)
Published: 2026-08-11
Source: https://osv.dev/vulnerability/CVE-2026-19550
Type: osv

## Details
A flaw was found in FreeIPA. The trust-fetch-domains command is gated by a read-only permission on the trust object rather than a trust-administration permission, allowing an authenticated, non-privileged IPA user to trigger a privileged Active Directory trust refresh using an attacker-supplied server and credentials, resulting in unauthorized, attacker-controlled modification of trusted-domain and ID-range identity data in the IPA LDAP directory.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://access.redhat.com/security/cve/CVE-2026-19550
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/19xxx/CVE-2026-19550.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-19550
- https://bugzilla.redhat.com/show_bug.cgi?id=2514019
