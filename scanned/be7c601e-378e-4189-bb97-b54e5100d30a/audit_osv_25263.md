# [M] Responder can Invoke Undefined Behavior in libspdm Requester

## Summary
Severity: Medium
Advisory: CVE-2023-32690
Aliases: GHSA-56h8-4gv5-jf2c
CVSS: 5.7 (CVSS:3.1/AV:A/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2023-06-01
Source: https://osv.dev/vulnerability/CVE-2023-32690
Type: osv

## Details
libspdm is a sample implementation that follows the DMTF SPDM specifications. Prior to versions 2.3.3 and 3.0, following a successful CAPABILITIES response, a libspdm Requester stores the Responder's CTExponent into its context without validation. If the Requester sends a request message that requires a cryptography operation by the Responder, such as CHALLENGE, libspdm will calculate the timeout value using the Responder's unvalidated CTExponent.

A patch is available in version 2.3.3. A workaround is also available. After completion of VCA, the Requester can check the value of the Responder's CTExponent. If it greater than or equal to 64, then the Requester can stop communication with the Responder.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/32xxx/CVE-2023-32690.json
- https://github.com/DMTF/libspdm/security/advisories/GHSA-56h8-4gv5-jf2c
- https://nvd.nist.gov/vuln/detail/CVE-2023-32690
- https://github.com/DMTF/libspdm/issues/2068
- https://github.com/DMTF/libspdm/pull/2069
