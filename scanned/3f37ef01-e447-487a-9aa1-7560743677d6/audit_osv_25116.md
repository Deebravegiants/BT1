# [C] DMTF-2023-0001: SPDM mutual authentication bypass

## Summary
Severity: Critical
Advisory: CVE-2023-31127
Aliases: GHSA-qw76-4v8p-xq9f
CVSS: 9.0 (CVSS:3.1/AV:A/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2023-05-08
Source: https://osv.dev/vulnerability/CVE-2023-31127
Type: osv

## Details
libspdm is a sample implementation that follows the DMTF SPDM specifications. A vulnerability has been identified in SPDM session establishment in libspdm prior to version 2.3.1. If a device supports both DHE session and PSK session with mutual
authentication, the attacker may be able to establish the session with `KEY_EXCHANGE` and `PSK_FINISH` to bypass the mutual authentication. This is most likely to happen when the Requester begins a session using one method (DHE, for example) and then uses the other method's finish (PSK_FINISH in this example) to establish the session. The session hashes would be expected to fail in this case, but the condition was not detected.

This issue only impacts the SPDM responder, which supports `KEY_EX_CAP=1 and `PSK_CAP=10b` at same time with mutual authentication requirement. The SPDM requester is not impacted. The SPDM responder is not impacted if `KEY_EX_CAP=0` or `PSK_CAP=0` or `PSK_CAP=01b`. The SPDM responder is not impacted if mutual authentication is not required.

libspdm 1.0, 2.0, 2.1, 2.2, 2.3 are all impacted. Older branches are not maintained, but users of the 2.3 branch may receive a patch in version 2.3.2. The SPDM specification (DSP0274) does not contain this vulnerability.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/31xxx/CVE-2023-31127.json
- https://github.com/DMTF/libspdm/security/advisories/GHSA-qw76-4v8p-xq9f
- https://nvd.nist.gov/vuln/detail/CVE-2023-31127
- https://github.com/DMTF/libspdm/pull/2006
- https://github.com/DMTF/libspdm/pull/2007
