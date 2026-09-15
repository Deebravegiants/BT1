# [M] Insufficient Session Expiration in Apache NiFi Registry

## Summary
Severity: Medium
Advisory: GHSA-rcwj-2hj2-vmjj
CVE: CVE-2020-9482
CWE: CWE-613
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2022-02-09
Source: https://github.com/advisories/GHSA-rcwj-2hj2-vmjj
Type: github-advisory

## Affected
- Maven: `org.apache.nifi.registry:nifi-registry-web-api` — affected >=0.1.0 <0.7.0

## Details
If NiFi Registry 0.1.0 to 0.5.0 uses an authentication mechanism other than PKI, when the user clicks Log Out, NiFi Registry invalidates the authentication token on the client side but not on the server side. This permits the user's client-side token to be used for up to 12 hours after logging out to make API requests to NiFi Registry.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-9482
- https://github.com/apache/nifi-registry/pull/259/commits/32f9352465e877d71ad7f85b70f2304ba620e133#diff-a72e640a2c41fe6fe8848066f6a588da2e9e76350bef287d7e145a231042c485
- https://github.com/apache/nifi-registry/pull/277/files/9f7f1c1b1095e3facdaa986435fa94eff78627dd
- https://github.com/apache/nifi-registry/commit/2881e29dce3a179f3e56069b82ef8cbb7bd8d85c
- https://nifi.apache.org/registry-security.html#CVE-2020-9482
