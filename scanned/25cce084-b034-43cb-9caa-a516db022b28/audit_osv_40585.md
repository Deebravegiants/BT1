# [M] Open edX LTI OAuth Replay Attack

## Summary
Severity: Medium
Advisory: CVE-2026-53636
Aliases: GHSA-6gm5-c49g-p3h9
CVSS: 4.7 (CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:C/C:L/I:L/A:N)
Published: 2026-09-02
Source: https://osv.dev/vulnerability/CVE-2026-53636
Type: osv

## Details
Open edX Platform enables the authoring and delivery of online learning at any scale. Prior to commit 3a5ac85, a security vulnerability has been identified in the Open edX LMS platform's LTI (Learning Tools Interoperability) Provider implementation. The validate_timestamp_and_nonce function in lms/djangoapps/lti_provider/signature_validator.py does not validate OAuth nonces or timestamps, allowing an attacker who captures a valid LTI launch request to replay it an unlimited number of times without detection. This issue has been patched via commit 3a5ac85.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53636.json
- https://github.com/openedx/openedx-platform/security/advisories/GHSA-6gm5-c49g-p3h9
- https://nvd.nist.gov/vuln/detail/CVE-2026-53636
- https://github.com/openedx/openedx-platform/commit/0a92cf25de8844bf840ffd5d18dcfd940031a2ba
- https://github.com/openedx/openedx-platform/commit/3a5ac856c79557c5c74d8b3e6578f289d7cceecd
- https://github.com/openedx/openedx-platform/commit/50af17b05d82a8c7e8e690cc2783a8a0ba330bc3
