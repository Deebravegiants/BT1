# [C] Kata Containers: Config Path Annotation Arbitrary File Loading

## Summary
Severity: Critical
Advisory: CVE-2026-50540
Aliases: GHSA-mp2j-xm59-qfgw
CVSS: 9.6 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:N)
Published: 2026-08-07
Source: https://osv.dev/vulnerability/CVE-2026-50540
Type: osv

## Details
Kata Containers is an open source project focusing on a standard implementation of lightweight Virtual Machines (VMs) that perform like containers. Prior to version 4.0.0, kata-runtime is vulnerable to host code execution via an unvalidated configuration path annotation. The runtime accepts an arbitrary io.katacontainers.config_path pod annotation and loads the referenced host TOML file without restriction. As a result, a pod user who can place a file at a host-visible path can supply a configuration that selects an attacker-controlled hypervisor or virtio-fs daemon binary, executing code as root on the host. This issue is fixed in version 4.0.0.

## References
- http://www.openwall.com/lists/oss-security/2026/08/23/3
- http://www.openwall.com/lists/oss-security/2026/08/24/1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/50xxx/CVE-2026-50540.json
- https://github.com/kata-containers/kata-containers/security/advisories/GHSA-mp2j-xm59-qfgw
- https://nvd.nist.gov/vuln/detail/CVE-2026-50540
- https://github.com/kata-containers/kata-containers/commit/03cc670076099530f4e1e9cb22849afdafb20f65
