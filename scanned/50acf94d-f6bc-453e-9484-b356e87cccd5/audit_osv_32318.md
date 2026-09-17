# [M] Zincati allows unprivileged access to rpm-ostree D-Bus `Deploy()` and `FinalizeDeployment()` methods

## Summary
Severity: Medium
Advisory: CVE-2025-27512
Aliases: GHSA-w6fv-6gcc-x825
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:P/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N/E:U)
Published: 2025-03-17
Source: https://osv.dev/vulnerability/CVE-2025-27512
Type: osv

## Details
Zincati is an auto-update agent for Fedora CoreOS hosts. Zincati ships a polkit rule which allows the `zincati` system user to use the actions `org.projectatomic.rpmostree1.deploy` to deploy updates to the system and `org.projectatomic.rpmostree1.finalize-deployment` to reboot the system into the deployed update. Since Zincati v0.0.24, this polkit rule contains a logic error which broadens access of those polkit actions to any unprivileged user rather than just the `zincati` system user. In practice, this means that any unprivileged user with access to the system D-Bus socket is able to deploy older Fedora CoreOS versions (which may have other known vulnerabilities). Note that rpm-ostree enforces that the selected version must be from the same branch the system is currently on so this cannot directly be used to deploy an attacker-controlled update payload. This primarily impacts users running untrusted workloads with access to the system D-Bus socket. Note that in general, untrusted workloads should not be given this access, whether containerized or not. By default, containers do not have access to the system D-Bus socket. The logic error is fixed in Zincati v0.0.30. A workaround is to manually add a following polkit rule, instructions for which are available in the GitHub Security Advisory.

## References
- https://github.com/coreos/zincati/releases/tag/v0.0.24
- https://github.com/coreos/zincati/releases/tag/v0.0.30
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/27xxx/CVE-2025-27512.json
- https://github.com/coreos/zincati/security/advisories/GHSA-w6fv-6gcc-x825
- https://nvd.nist.gov/vuln/detail/CVE-2025-27512
- https://github.com/coreos/zincati/commit/01d8e89f799e6ba21bdf7dc668abce23bd0d8f78
- https://github.com/coreos/zincati/commit/28a43aa2c1edda091ba659677d73c13e6e3ea99d
