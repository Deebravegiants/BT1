# [M] HL7 FHIR IG Publisher potentially exposes GitHub repo user and credential information

## Summary
Severity: Medium
Advisory: GHSA-6729-95v3-pjc2
CVE: CVE-2025-24363
CWE: CWE-200
Ecosystem: Maven
CVSS: CVSS:3.1/AV:L/AC:L/PR:H/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2025-01-24
Source: https://github.com/advisories/GHSA-6729-95v3-pjc2
Type: github-advisory

## Affected
- Maven: `org.hl7.fhir.publisher:org.hl7.fhir.publisher.core` — affected >=0 <1.8.9
- Maven: `org.hl7.fhir.publisher:org.hl7.fhir.publisher.cli` — affected >=0 <1.8.9

## Details
### Impact
In CI contexts, the IG Publisher CLI uses git commands to determine the URL of the originating repo. If the repo was cloned, or otherwise set to use a repo that uses a username and credential based URL, the entire URL will be included in the built Implementation Guide, exposing username and credential. This does not impact users that clone public repos without credentials, such as those using the auto-ig-build continuous integration infrastructure.

### Patches
This problem has been patched in release [1.8.9](https://github.com/HL7/fhir-ig-publisher/releases/tag/1.8.9)

### Workarounds
Users should update to 1.8.9 or the latest release 

OR 

Users should ensure the IG repo they are publishing does not have username or credentials included in the `origin` URL. Running the command `git remote origin url` should return a URL that contains no username, password, or token.

OR

Users should run the IG Publisher CLI with the `-repo` parameter and specify a URL that contains no username, password, or token.

## References
- https://github.com/HL7/fhir-ig-publisher/security/advisories/GHSA-6729-95v3-pjc2
- https://nvd.nist.gov/vuln/detail/CVE-2025-24363
- https://github.com/HL7/fhir-ig-publisher/commit/d968694b7dd041640efab5414d7077d5028569f7
- https://github.com/HL7/fhir-ig-publisher
- https://github.com/HL7/fhir-ig-publisher/releases/tag/1.8.9
