# [H] Arduino Create Agent path traversal - local privilege escalation vulnerability

## Summary
Severity: High
Advisory: GHSA-75j7-w798-cwwx
CVE: CVE-2023-43802
CWE: CWE-22, CWE-35
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:L (CVSS_V3)
Published: 2023-10-18
Source: https://github.com/advisories/GHSA-75j7-w798-cwwx
Type: github-advisory

## Affected
- Go: `github.com/arduino/arduino-create-agent` — affected >=0 <1.3.3

## Details
### Impact
The vulnerability affects the endpoint `/upload` which handles request with the `filename` parameter.
A user who has the ability to perform HTTP requests to the localhost interface, or is able to bypass the CORS configuration, can escalate his privileges to those of the user running the Arduino Create Agent service via a crafted HTTP POST request.
Further details are available in the references.

### Fixed Version
* `1.3.3`


### References
The issue was reported by Nozomi Networks Labs. Further details are available at the following URL:
* https://www.nozominetworks.com/blog/security-flaws-affect-a-component-of-the-arduino-create-cloud-ide

## References
- https://github.com/arduino/arduino-create-agent/security/advisories/GHSA-75j7-w798-cwwx
- https://nvd.nist.gov/vuln/detail/CVE-2023-43802
- https://github.com/arduino/arduino-create-agent
- https://github.com/arduino/arduino-create-agent/releases/tag/1.3.3
- https://www.nozominetworks.com/blog/security-flaws-affect-a-component-of-the-arduino-create-cloud-ide
