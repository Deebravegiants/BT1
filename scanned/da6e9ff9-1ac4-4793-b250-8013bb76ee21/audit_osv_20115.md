# [H] CVE-2021-3101

## Summary
Severity: High
Advisory: CVE-2021-3101
Aliases: GHSA-qfhv-c5cc-mhgp
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2022-04-19
Source: https://osv.dev/vulnerability/CVE-2021-3101
Type: osv

## Details
Hotdog, prior to v1.0.1, did not mimic the capabilities or the SELinux label of the target JVM process. This would allow a container to gain full privileges on the host, bypassing restrictions set on the container.

## References
- https://github.com/bottlerocket-os/hotdog/security/advisories/GHSA-qfhv-c5cc-mhgp
- https://unit42.paloaltonetworks.com/aws-log4shell-hot-patch-vulnerabilities
