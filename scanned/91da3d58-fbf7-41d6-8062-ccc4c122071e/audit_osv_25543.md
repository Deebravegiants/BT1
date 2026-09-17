# [H] Subscription-manager: inadequate authorization of com.redhat.rhsm1 d-bus interface allows local users to modify configuration

## Summary
Severity: High
Advisory: CVE-2023-3899
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-08-23
Source: https://osv.dev/vulnerability/CVE-2023-3899
Type: osv

## Details
A vulnerability was found in subscription-manager that allows local privilege escalation due to inadequate authorization. The D-Bus interface com.redhat.RHSM1 exposes a significant number of methods to all users that could change the state of the registration. By using the com.redhat.RHSM1.Config.SetAll() method, a low-privileged local user could tamper with the state of the registration, by unregistering the system or by changing the current entitlements. This flaw allows an attacker to set arbitrary configuration directives for /etc/rhsm/rhsm.conf, which can be abused to cause a local privilege escalation to an unconfined root.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/FJHKSBBZRDFOBNDU35FUKMYQIQYT6UJQ/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/ZDIHGNLS3TZVX7X2F735OKI4KXPY4AH6/
- https://access.redhat.com/errata/RHSA-2023:4701
- https://access.redhat.com/errata/RHSA-2023:4702
- https://access.redhat.com/errata/RHSA-2023:4703
- https://access.redhat.com/errata/RHSA-2023:4704
- https://access.redhat.com/errata/RHSA-2023:4705
- https://access.redhat.com/errata/RHSA-2023:4706
- https://access.redhat.com/errata/RHSA-2023:4707
- https://access.redhat.com/errata/RHSA-2023:4708
- https://access.redhat.com/security/cve/CVE-2023-3899
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/3xxx/CVE-2023-3899.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-3899
- https://bugzilla.redhat.com/show_bug.cgi?id=2225407
