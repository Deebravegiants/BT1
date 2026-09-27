# [H] ndsudo: local privilege escalation via untrusted search path

## Summary
Severity: High
Advisory: CVE-2024-32019
Aliases: GHSA-pmhq-4cxq-wj93
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2024-04-12
Source: https://osv.dev/vulnerability/CVE-2024-32019
Type: osv

## Details
Netdata is an open source observability tool. In affected versions the `ndsudo` tool shipped with affected versions of the Netdata Agent allows an attacker to run arbitrary programs with root permissions. The `ndsudo` tool is packaged as a `root`-owned executable with the SUID bit set. It only runs a restricted set of external commands, but its search paths are supplied by the `PATH` environment variable. This allows an attacker to control where `ndsudo` looks for these commands, which may be a path the attacker has write access to. This may lead to local privilege escalation. This vulnerability has been addressed in versions 1.45.3 and 1.45.2-169. Users are advised to upgrade. There are no known workarounds for this vulnerability.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/32xxx/CVE-2024-32019.json
- https://github.com/netdata/netdata/security/advisories/GHSA-pmhq-4cxq-wj93
- https://nvd.nist.gov/vuln/detail/CVE-2024-32019
- https://github.com/netdata/netdata/pull/17377
