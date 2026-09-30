# [C] OS command injection in Gipsy

## Summary
Severity: Critical
Advisory: CVE-2023-30621
Aliases: GHSA-6cw6-r8pg-j7wh
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-04-21
Source: https://osv.dev/vulnerability/CVE-2023-30621
Type: osv

## Details
Gipsy is a multi-purpose discord bot which aim to be as modular and user-friendly as possible. In versions prior to 1.3 users can run command on the host machine with sudoer permission. The `!ping` command when provided with an IP or hostname used to run a bash `ping <IP>` without verification that the IP or hostname was legitimate. This command was executed with root permissions and may lead to arbitrary command injection on the host server. Users are advised to upgrade. There are no known workarounds for this vulnerability.

## References
- https://github.com/Gunivers/Gipsy/pull/24/commits/716818e967069f144aae66d51464b237c22b6cdf
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/30xxx/CVE-2023-30621.json
- https://github.com/Curiosity-org/Gipsy/security/advisories/GHSA-6cw6-r8pg-j7wh
- https://nvd.nist.gov/vuln/detail/CVE-2023-30621
- https://github.com/Gunivers/Gipsy/pull/24
