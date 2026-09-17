# [C] LXD arbitrary lxc.conf directive injection via NVIDIA instance configuration

## Summary
Severity: Critical
Advisory: CVE-2026-63298
Aliases: GHSA-vfh7-q59q-54v2
CVSS: 9.9 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-08-12
Source: https://osv.dev/vulnerability/CVE-2026-63298
Type: osv

## Details
An improper neutralization of special elements vulnerability in LXD's NVIDIA instance configuration handling allows an authenticated attacker to inject arbitrary configuration directives. By supplying newline characters within the 'nvidia.driver.capabilities' or 'nvidia.require.*' configuration values, an attacker can manipulate the generated lxc.conf file. This flaw enables the attacker to execute arbitrary code on the host system with the privileges of the LXD daemon.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/63xxx/CVE-2026-63298.json
- https://github.com/canonical/lxd/security/advisories/GHSA-vfh7-q59q-54v2
- https://nvd.nist.gov/vuln/detail/CVE-2026-63298
- https://github.com/canonical/lxd
