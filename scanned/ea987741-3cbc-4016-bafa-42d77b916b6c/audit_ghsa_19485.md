# [M] io.jmix.localfs:jmix-localfs has a Path Traversal in Local File Storage

## Summary
Severity: Medium
Advisory: GHSA-jx4g-3xqm-62vh
CVE: CVE-2025-32950
CWE: CWE-22, CWE-35
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2025-04-22
Source: https://github.com/advisories/GHSA-jx4g-3xqm-62vh
Type: github-advisory

## Affected
- Maven: `io.jmix.localfs:jmix-localfs` — affected >=1.0.0 <1.6.2
- Maven: `io.jmix.localfs:jmix-localfs` — affected >=2.0.0 <2.4.0

## Details
### Impact

Attackers could manipulate the `FileRef` parameter to access files on the system where the Jmix application is deployed, provided the application server has the necessary permissions. This can be accomplished either by modifying the `FileRef` directly in the database or by supplying a harmful value in the `fileRef` parameter of the `/files` endpoint of the generic REST API.

Arbitrary file reading on the operating system where the Jmix process is running.

The severity of the vulnerability is mitigated by the fact that the application UI and the generic REST API are typically accessible only to authenticated users. Additionally, the `/files` endpoint in Jmix requires specific permissions and is disabled by default.

### Workarounds
A workaround for those who are unable to upgrade: [Fix Path Traversal in Jmix Application](https://docs.jmix.io/jmix/files-vulnerabilities.html#fix-path-traversal-in-jmix-application).

### Credit
Cai, Qi Qi of Siemens China Cybersecurity Testing Center - Shadowless Lab

## References
- https://github.com/jmix-framework/jmix/security/advisories/GHSA-jx4g-3xqm-62vh
- https://nvd.nist.gov/vuln/detail/CVE-2025-32950
- https://github.com/jmix-framework/jmix/issues/3804
- https://github.com/jmix-framework/jmix/issues/3836
- https://github.com/jmix-framework/jmix/commit/6a66aa3adb967159a30d703e80403406f4c8f7a2
- https://github.com/jmix-framework/jmix/commit/c589ef4e2b25620770b8036f4ad05f1a6250cb6a
- https://github.com/jmix-framework/jmix/commit/cc97e6ff974b9e7af8160fab39cc5866169daa37
- https://github.com/jmix-framework/jmix/commit/f4e6fb05bd245cf36f3e9319aaa0fcd540d024aa
- https://docs.jmix.io/jmix/files-vulnerabilities.html
- https://docs.jmix.io/jmix/files-vulnerabilities.html#fix-path-traversal-in-jmix-application
- https://github.com/jmix-framework/jmix
