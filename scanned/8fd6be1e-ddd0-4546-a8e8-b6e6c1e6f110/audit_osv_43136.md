# [H] OpenSignLabs OpenSign - Insecure Direct Object Reference

## Summary
Severity: High
Advisory: CVE-2026-72543
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-08-11
Source: https://osv.dev/vulnerability/CVE-2026-72543
Type: osv

## Details
An insecure direct object reference vulnerability in OpenSignLabs OpenSign through 2.37.0 allows unauthenticated remote attackers to retrieve any contact record via the getcontact Parse cloud function. The function executes with useMasterKey and performs no authentication or authorization checks before returning the requested contact object. An attacker can enumerate and read all contact records including personally identifiable information without credentials.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72543.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72543
- https://github.com/OpenSignLabs/OpenSign
