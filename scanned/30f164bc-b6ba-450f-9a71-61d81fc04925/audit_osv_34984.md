# [C] CVE-2025-67109

## Summary
Severity: Critical
Advisory: CVE-2025-67109
CVSS: 10.0 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2025-12-23
Source: https://osv.dev/vulnerability/CVE-2025-67109
Type: osv

## Details
Improper verification of the time certificate in Eclipse Cyclone DDS before v0.10.5 allows attackers to bypass certificate checks and execute commands with System privileges.

## References
- https://gist.github.com/lkloliver/669e15bc7e6194133e4ee1026ce157e6
- https://github.com/eclipse-cyclonedds/cyclonedds/blob/master/src/ddsrt/src/time/posix/time.c#L28
- https://github.com/eclipse-cyclonedds/cyclonedds/blob/master/src/security/builtin_plugins/authentication/src/auth_utils.c#L84
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/67xxx/CVE-2025-67109.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-67109
