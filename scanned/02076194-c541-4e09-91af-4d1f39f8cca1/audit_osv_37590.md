# [H] himmelblaud-tasks: local privilege escalation via /tmp symlink attack on Kerberos ccache

## Summary
Severity: High
Advisory: CVE-2026-31979
Aliases: GHSA-44wm-q286-ghq3
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-03-11
Source: https://osv.dev/vulnerability/CVE-2026-31979
Type: osv

## Details
Himmelblau is an interoperability suite for Microsoft Azure Entra ID and Intune. Prior to 3.1.0 and 2.3.8, the himmelblaud-tasks daemon, running as root, writes Kerberos cache files under /tmp/krb5cc_<uid> without symlink protections. Since commit 87a51ee, PrivateTmp is explicitly removed from the tasks daemon's systemd hardening, exposing it to the host /tmp. A local user can exploit this via symlink attacks to chown or overwrite arbitrary files, achieving local privilege escalation. This vulnerability is fixed in 3.1.0 and 2.3.8.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31979.json
- https://github.com/himmelblau-idm/himmelblau/security/advisories/GHSA-44wm-q286-ghq3
- https://nvd.nist.gov/vuln/detail/CVE-2026-31979
