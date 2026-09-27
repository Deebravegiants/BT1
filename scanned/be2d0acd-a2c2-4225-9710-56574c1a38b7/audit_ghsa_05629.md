# [H] Spinnaker vulnerable to SSRF due to improper restrictions on http from user input

## Summary
Severity: High
Advisory: GHSA-vrjc-q2fh-6x9h
CVE: CVE-2025-61916
CWE: CWE-20, CWE-523, CWE-918
Ecosystem: Maven
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:L/A:L (CVSS_V3)
Published: 2026-01-05
Source: https://github.com/advisories/GHSA-vrjc-q2fh-6x9h
Type: github-advisory

## Affected
- Maven: `io.spinnaker.clouddriver:clouddriver-artifacts` — affected >=0 <2025.1.6
- Maven: `io.spinnaker.clouddriver:clouddriver-artifacts` — affected >=2025.2.0 <2025.2.3

## Details
### Impact
The primary impact is allowing users to fetch data from a remote URL.  This data can be then injected into Spinnaker pipelines via helm or other methods to extract things LIKE idmsv1 authentication data.  This ALSO includes calling INTERNAL Spinnaker API's via a get and similar endpoints.  Further, depending upon the artifact configuration, auth data may be exposed to arbitrary endpoints (e.g. GitHub auth headers) leading to credentials exposure.   

To trigger this, a Spinnaker installation MUST have:
* An artifact enabled that allows user input.  This includes GitHub file artifacts, BitBucket, GitLab, HTTP artifacts and similar artifact providers.  JUST enabling the http artifact provider will add a "no-auth" http provider that could be used to extract link local data (e.g. AWS Metadata information).
* A system that can consume the output of these artifacts.  E.g. Rosco helm can use this to fetch values data.  K8s account manifests if the API returns JSON can be used to inject that data into the pipeline itself though the pipeline would fail.

To note, due to the way the URLs are viable to be injected, CERTAIN systems can be used to provide DOS attacks on Spinnaker itself.  These would NOT compromise the system per se, given restarts and timeout configuration, but could lead to internal attacks by a Spinnaker user against Spinnaker services.  An example is that an artifact fetch reference could return an infinite response data feed or similar that can act as a DOS attack.  It's recommended to set strong limits on the various http limits AND artifact URLs to known valid URLs. 

### Patches
Fixed in clouddriver versiosn 2025.2.3, 2025.1.5, 2025.0.9.  Impacts all prior Spinnaker releases.

### Workarounds
Disable HTTP account types that allow user input of a given URL.  This is probably not feasible in MOST cases.  Git, Docker and other artifact account types with explicit URL configurations bypass this limitation and should be safe as they limit artifact URL loading.

Alternatively using one of the various vendors which provide OPA policies to restrict pipelines from accessing or saving a pipeline with invalid URLs.

## References
- https://github.com/spinnaker/spinnaker/security/advisories/GHSA-vrjc-q2fh-6x9h
- https://nvd.nist.gov/vuln/detail/CVE-2025-61916
- https://github.com/spinnaker/spinnaker
