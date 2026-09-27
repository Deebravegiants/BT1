# [H] Keylime registrar and (untrusted) Agent can be bypassed by an attacker

## Summary
Severity: High
Advisory: GHSA-f4r5-q63f-gcww
CVE: CVE-2023-38201
CWE: CWE-639
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2023-09-06
Source: https://github.com/advisories/GHSA-f4r5-q63f-gcww
Type: github-advisory

## Affected
- PyPI: `keylime` — affected >=0 <7.5.0

## Details
### Impact

A security issue was found in the Keylime `registrar` code which allows an attacker to effectively bypass the challenge-response protocol used to verify that an `agent` has indeed access to an AIK which in indeed related to the EK.

When an `agent` starts up, it will contact a `registrar` and provide a public EK and public AIK, in addition to the EK Certificate. This `registrar` will then challenge the `agent` to decrypt a challenge encrypted with the EK. 

When receiving the wrong "auth_tag" back from the `agent` during activation, the `registrar` answers with an error message that contains the expected correct "auth_tag" (an HMAC which is calculated within the `registrar` for checking). An attacker could simply record the correct expected "auth_tag" from the HTTP error message and perform the activate call again with the correct expected "auth_tag" for the `agent`.

The security issue allows an attacker to pass the challenge-response protocol during registration with (almost) arbitrary registration data. In particular, the attacker can provide a valid EK Certificate and EK, which passes verification by the `tenant` (or `registrar`), while using a compromised AIK, which is stored unprotected outside the TPM and is unrelated to former two. The attacker then deliberately fails the initial activation call to get to know the correct "auth_tag" and then provides it in a subsequent activation call. This results in an `agent` which is (incorrectly) registered with a valid EK Certificate, but with a compromised/unrelated AIK.

### Patches
Users should upgrade to release 7.5.0

## References
- https://github.com/keylime/keylime/security/advisories/GHSA-f4r5-q63f-gcww
- https://nvd.nist.gov/vuln/detail/CVE-2023-38201
- https://github.com/keylime/keylime/commit/9e5ac9f25cd400b16d5969f531cee28290543f2a
- https://access.redhat.com/errata/RHSA-2023:5080
- https://access.redhat.com/security/cve/CVE-2023-38201
- https://bugzilla.redhat.com/show_bug.cgi?id=2222693
- https://github.com/keylime/keylime
- https://github.com/pypa/advisory-database/tree/main/vulns/keylime/PYSEC-2023-160.yaml
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/ZIZZB5NHNCS5D2AEH3ZAO6OQC72IK7WS
