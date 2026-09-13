# [H] Freeipa: delegation rules allow a proxy service to impersonate any user to access another target service

## Summary
Severity: High
Advisory: CVE-2024-2698
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-06-12
Source: https://osv.dev/vulnerability/CVE-2024-2698
Type: osv

## Details
A vulnerability was found in FreeIPA in how the initial implementation of MS-SFU by MIT Kerberos was missing a condition for granting the "forwardable" flag on S4U2Self tickets. Fixing this mistake required adding a special case for the check_allowed_to_delegate() function: If the target service argument is NULL, then it means the KDC is probing for general constrained delegation rules and not checking a specific S4U2Proxy request.

In FreeIPA 4.11.0, the behavior of ipadb_match_acl() was modified to match the changes from upstream MIT Kerberos 1.20. However, a mistake resulting in this mechanism applies in cases where the target service argument is set AND where it is unset. This results in S4U2Proxy requests being accepted regardless of whether or not there is a matching service delegation rule.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/WT3JL7JQDIAFKKEFARWYES7GZNWGQNCI/
- https://www.freeipa.org/release-notes/4-12-1.html
- https://access.redhat.com/errata/RHSA-2024:3754
- https://access.redhat.com/errata/RHSA-2024:3755
- https://access.redhat.com/errata/RHSA-2024:3757
- https://access.redhat.com/errata/RHSA-2024:3759
- https://access.redhat.com/security/cve/CVE-2024-2698
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/2xxx/CVE-2024-2698.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-2698
- https://bugzilla.redhat.com/show_bug.cgi?id=2270353
- https://github.com/freeipa/freeipa
