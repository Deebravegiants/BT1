# [M] Arduino Create Agent path traversal - arbitrary file deletion vulnerability

## Summary
Severity: Medium
Advisory: GHSA-m5jc-r4gf-c6p8
CVE: CVE-2023-43803
CWE: CWE-22, CWE-35
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:L (CVSS_V3)
Published: 2023-10-18
Source: https://github.com/advisories/GHSA-m5jc-r4gf-c6p8
Type: github-advisory

## Affected
- Go: `github.com/arduino/arduino-create-agent` — affected >=0 <1.3.3

## Details
### Impact
The vulnerability affects the endpoint `/v2/pkgs/tools/installed` and the way it handles plugin names supplied as user input.
A user who has the ability to perform HTTP requests to the localhost interface, or is able to bypass the CORS configuration, can delete arbitrary files or folders belonging to the user that runs the Arduino Create Agent via a crafted HTTP POST request.
Further details are available in the references.

### Fixed Version
* `1.3.3`

### References
The issue was reported by Nozomi Networks Labs. Further details on the issue are available at the following URL:
* https://www.nozominetworks.com/blog/security-flaws-affect-a-component-of-the-arduino-create-cloud-ide

## References
- https://github.com/arduino/arduino-create-agent/security/advisories/GHSA-m5jc-r4gf-c6p8
- https://nvd.nist.gov/vuln/detail/CVE-2023-43803
- https://github.com/arduino/arduino-create-agent
- https://github.com/arduino/arduino-create-agent/releases/tag/1.3.3
- https://lists.debian.org/debian-lts-announce/2023/11/msg00005.html
- https://www.nozominetworks.com/blog/security-flaws-affect-a-component-of-the-arduino-create-cloud-ide
