# [M] OpenCTI bypass of protected attribute update

## Summary
Severity: Medium
Advisory: CVE-2025-24887
Aliases: GHSA-8262-pw2q-5qc3, PYSEC-2025-178
CVSS: 6.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L)
Published: 2025-04-30
Source: https://osv.dev/vulnerability/CVE-2025-24887
Type: osv

## Details
OpenCTI is an open-source cyber threat intelligence platform. In versions starting from 6.4.8 to before 6.4.10, the allow/deny lists can be bypassed, allowing a user to change attributes that are intended to be unmodifiable by the user. It is possible to toggle the `external` flag on/off and change the own token value for a user. It is also possible to edit attributes that are not in the allow list, such as `otp_qr` and `otp_activated`. If external users exist in the OpenCTI setup and the information about these users identities is sensitive, the above vulnerabilities can be used to enumerate existing user accounts as a standard low privileged user. This issue has been patched in version 6.4.10.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/24xxx/CVE-2025-24887.json
- https://github.com/OpenCTI-Platform/opencti/security/advisories/GHSA-8262-pw2q-5qc3
- https://nvd.nist.gov/vuln/detail/CVE-2025-24887
