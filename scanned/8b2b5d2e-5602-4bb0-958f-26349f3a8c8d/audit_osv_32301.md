# [C] CVE-2025-27364

## Summary
Severity: Critical
Advisory: CVE-2025-27364
CVSS: 10.0 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2025-02-24
Source: https://osv.dev/vulnerability/CVE-2025-27364
Type: osv

## Details
In MITRE Caldera through 4.2.0 and 5.0.0 before 35bc06e, a Remote Code Execution (RCE) vulnerability was found in the dynamic agent (implant) compilation functionality of the server. This allows remote attackers to execute arbitrary code on the server that Caldera is running on via a crafted web request to the Caldera server API used for compiling and downloading of Caldera's Sandcat or Manx agent (implants). This web request can use the gcc -extldflags linker flag with sub-commands.

## References
- https://github.com/mitre/caldera/pull/3131/commits/61de40f92a595bed462372a5e676c2e5a32d1050
- https://github.com/mitre/caldera/security
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/27xxx/CVE-2025-27364.json
- https://medium.com/@mitrecaldera/mitre-caldera-security-advisory-remote-code-execution-cve-2025-27364-5f679e2e2a0e
- https://nvd.nist.gov/vuln/detail/CVE-2025-27364
- https://github.com/mitre/caldera/commit/35bc06e42e19fe7efbc008999b9f993b1b7109c0
- https://github.com/mitre/caldera/pull/3129
- https://github.com/mitre/caldera/releases
