# [M] Undertow: learningpushhandler can lead to remote memory dos attacks

## Summary
Severity: Medium
Advisory: CVE-2024-3653
Aliases: GHSA-ch7q-gpff-h9hp
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2024-07-08
Source: https://osv.dev/vulnerability/CVE-2024-3653
Type: osv

## Details
A vulnerability was found in Undertow. This issue requires enabling the learning-push handler in the server's config, which is disabled by default, leaving the maxAge config in the handler unconfigured. The default is -1, which makes the handler vulnerable. If someone overwrites that config, the server is not subject to the attack. The attacker needs to be able to reach the server with a normal HTTP request.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://access.redhat.com/jbossnetwork/restricted/listSoftware.html
- https://access.redhat.com/errata/RHSA-2024:4392
- https://access.redhat.com/errata/RHSA-2024:5143
- https://access.redhat.com/errata/RHSA-2024:5144
- https://access.redhat.com/errata/RHSA-2024:5145
- https://access.redhat.com/errata/RHSA-2024:5147
- https://access.redhat.com/errata/RHSA-2024:6437
- https://access.redhat.com/security/cve/CVE-2024-3653
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/3xxx/CVE-2024-3653.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-3653
- https://security.netapp.com/advisory/ntap-20240828-0002/
- https://bugzilla.redhat.com/show_bug.cgi?id=2274437
- https://github.com/undertow-io/undertow
