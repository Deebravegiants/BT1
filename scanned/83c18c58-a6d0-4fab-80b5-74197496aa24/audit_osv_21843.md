# [H] Hotdog Container Escape

## Summary
Severity: High
Advisory: CVE-2022-0071
Aliases: GHSA-jr96-7frv-3mpj
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2022-04-19
Source: https://osv.dev/vulnerability/CVE-2022-0071
Type: osv

## Details
Incomplete fix for CVE-2021-3101. Hotdog, prior to v1.0.2, did not mimic the resource limits, device restrictions, or syscall filters of the target JVM process. This would allow a container to exhaust the resources of the host, modify devices, or make syscalls that would otherwise be blocked.

## References
- https://unit42.paloaltonetworks.com/aws-log4shell-hot-patch-vulnerabilities
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/0xxx/CVE-2022-0071.json
- https://github.com/bottlerocket-os/hotdog/security/advisories/GHSA-jr96-7frv-3mpj
- https://nvd.nist.gov/vuln/detail/CVE-2022-0071
