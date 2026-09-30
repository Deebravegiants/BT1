# [H] Podman: Malformed Image can trick podman run into leaking host environment variables into the container

## Summary
Severity: High
Advisory: CVE-2026-57231
Aliases: GHSA-4hq8-gpf5-8p68
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-06-26
Source: https://osv.dev/vulnerability/CVE-2026-57231
Type: osv

## Details
Podman is a tool for managing OCI containers and pods. From 1.8.1 until 5.8.4, a container image that contains a environment variable with just a key and no value can trick podman into passing that variable from the host into the container. This is made worse by the fact that using an asterisk (*) will cause podman to pass all host variables into the container. So essentially a malicious image can exfiltrate all podman environment variables that are set in the session from where the container is launched. This vulnerability is fixed in 5.8.4 and 6.0.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/57xxx/CVE-2026-57231.json
- https://github.com/podman-container-tools/podman/security/advisories/GHSA-4hq8-gpf5-8p68
- https://nvd.nist.gov/vuln/detail/CVE-2026-57231
- https://github.com/podman-container-tools/podman/commit/6c431b73dbf8e4b20b778644d7a80caebdb75050
