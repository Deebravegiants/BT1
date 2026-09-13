# [C] step-ca has Unauthenticated Certificate Issuance via SCEP UpdateReq (MessageType=18)

## Summary
Severity: Critical
Advisory: GHSA-q4r8-xm5f-56gw
CVE: CVE-2026-30836
CWE: CWE-287, CWE-295
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2026-03-19
Source: https://github.com/advisories/GHSA-q4r8-xm5f-56gw
Type: github-advisory

## Affected
- Go: `github.com/smallstep/certificates` — affected >=0 <0.30.0

## Details
## Summary

An attacker can force a Step CA SCEP provisioner to create certificates without completing certain protocol authorization checks.

## Details

SCEP requests carry a message type. On receipt of a SCEP request, Step CA starts processing it by parsing its contents. Message types that were considered valid, but not explicitly supported in Step CA, would result in getting parsed successfully. While processing the parsed SCEP message, authorization logic would be skipped for the non-supported message types.

As a result, the request would be treated as authorized, bypassing the authorization checks normally enforced as part of the SCEP protocol and its implementation in Step CA.

Authorization webhooks and regular CA policies, such as allowed names and restrictions on certificate validity periods, remain in place.

## Mitigations

If you are unable to upgrade to v0.30.0 or newer, the attack can be mitigated by (temporarily) disabling or removing SCEP provisioners, or restricting access to SCEP provisioners to trusted clients only.

## Fix

In v0.30.0, additional validation was added to SCEP provisioners, so that they reject unsupported message types.

## Acknowledgements

This issue was identified and reported by Prasanth Sundararajan.

## Embargo List

If your organization runs Step CA in production and would like advance, embargoed notification of future security updates, visit https://u.step.sm/disclosure to request inclusion on our embargo list.

Stay safe, and thank you for helping us keep the ecosystem secure.

If you have urgent questions, please contact [security@smallstep.com](mailto:security@smallstep.com).

## References
- https://github.com/smallstep/certificates/security/advisories/GHSA-q4r8-xm5f-56gw
- https://nvd.nist.gov/vuln/detail/CVE-2026-30836
- https://github.com/smallstep/certificates/commit/e6da031d5125cfd99fe9a26f74bb41e4dacca4ef
- https://github.com/smallstep/certificates
- https://github.com/smallstep/certificates/releases/tag/v0.30.0-rc7
