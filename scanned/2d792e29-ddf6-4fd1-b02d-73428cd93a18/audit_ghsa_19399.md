# [M] io.jmix.localfs:jmix-localfs affected by DoS in the Local File Storage

## Summary
Severity: Medium
Advisory: GHSA-f3gv-cwwh-758m
CVE: CVE-2025-32952
CWE: CWE-770
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-04-22
Source: https://github.com/advisories/GHSA-f3gv-cwwh-758m
Type: github-advisory

## Affected
- Maven: `io.jmix.localfs:jmix-localfs` — affected >=1.0.0 <1.6.2
- Maven: `io.jmix.localfs:jmix-localfs` — affected >=2.0.0 <2.4.0

## Details
### Impact

The local file storage implementation does not restrict the size of uploaded files. An attacker could exploit this by uploading excessively large files, potentially causing the server to run out of space and return HTTP 500 error, resulting in a denial of service.

The severity of the vulnerability is mitigated by the fact that the application UI and the generic REST API are typically accessible only to authenticated users. Additionally, the /files endpoint in Jmix requires specific permissions and is disabled by default. 

### Patches

The problem has been fixed in Jmix 1.6.2+ and 2.4.0+.

### Workarounds

A workaround for those who are unable to upgrade: [Disable Files Endpoint in Jmix Application](https://docs.jmix.io/jmix/files-vulnerabilities.html#disable-files-endpoint-in-jmix-application).

## References
- https://github.com/jmix-framework/jmix/security/advisories/GHSA-f3gv-cwwh-758m
- https://nvd.nist.gov/vuln/detail/CVE-2025-32952
- https://github.com/jmix-framework/jmix/issues/3804
- https://github.com/jmix-framework/jmix/issues/3836
- https://github.com/jmix-framework/jmix/commit/6a66aa3adb967159a30d703e80403406f4c8f7a2
- https://github.com/jmix-framework/jmix/commit/c589ef4e2b25620770b8036f4ad05f1a6250cb6a
- https://github.com/jmix-framework/jmix/commit/cc97e6ff974b9e7af8160fab39cc5866169daa37
- https://github.com/jmix-framework/jmix/commit/f4e6fb05bd245cf36f3e9319aaa0fcd540d024aa
- https://docs.jmix.io/jmix/files-vulnerabilities.html
- https://docs.jmix.io/jmix/files-vulnerabilities.html#disable-files-endpoint-in-jmix-application
- https://github.com/jmix-framework/jmix
