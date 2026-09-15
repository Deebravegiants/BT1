# [H] Pam: improper hostname interpretation in pam_access leads to access control bypass

## Summary
Severity: High
Advisory: CVE-2024-10963
CVSS: 7.4 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2024-11-07
Source: https://osv.dev/vulnerability/CVE-2024-10963
Type: osv

## Details
A flaw was found in pam_access, where certain rules in its configuration file are mistakenly treated as hostnames. This vulnerability allows attackers to trick the system by pretending to be a trusted hostname, gaining unauthorized access. This issue poses a risk for systems that rely on this feature to control who can access certain services or terminals.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://catalog.redhat.com/software/containers/
- https://github.com/linux-pam/linux-pam/
- https://access.redhat.com/errata/RHSA-2024:10232
- https://access.redhat.com/errata/RHSA-2024:10244
- https://access.redhat.com/errata/RHSA-2024:10379
- https://access.redhat.com/errata/RHSA-2024:10518
- https://access.redhat.com/errata/RHSA-2024:10528
- https://access.redhat.com/errata/RHSA-2024:10852
- https://access.redhat.com/errata/RHSA-2024:6122
- https://access.redhat.com/security/cve/CVE-2024-10963
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/10xxx/CVE-2024-10963.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-10963
- https://bugzilla.redhat.com/show_bug.cgi?id=2324291
- https://github.com/linux-pam/linux-pam/issues/834
- https://github.com/linux-pam/linux-pam/pull/835
