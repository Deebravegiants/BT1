# [C] Step CA Has Authorization Bypass in ACME and SCEP Provisioners

## Summary
Severity: Critical
Advisory: GHSA-h8cp-697h-8c8p
CVE: CVE-2025-44005
CWE: CWE-306
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2025-12-03
Source: https://github.com/advisories/GHSA-h8cp-697h-8c8p
Type: github-advisory

## Affected
- Go: `github.com/smallstep/certificates` — affected >=0 <0.29.0

## Details
## Summary

A security fix is now available for Step CA that resolves a vulnerability affecting deployments configured with ACME and/or SCEP provisioners.
All operators running these provisioners should upgrade to the latest release (`v0.29.0`) immediately.

The issue was discovered and disclosed by a research team during a security review. There is no evidence of active exploitation.

To limit exploitation risk during a coordinated disclosure window, we are withholding detailed technical information for now. A full write-up will be published in several weeks.

---

## Embargo List

If your organization runs Step CA in production and would like advance, embargoed notification of future security updates, visit https://u.step.sm/disclosure to request inclusion on our embargo list.

---

## Acknowledgements

This issue was identified and reported by Stephen Kubik of the Cisco Advanced Security Initiatives Group (ASIG)

---

Stay safe, and thank you for helping us keep the ecosystem secure.

## References
- https://github.com/smallstep/certificates/security/advisories/GHSA-h8cp-697h-8c8p
- https://github.com/smallstep/certificates/commit/1011f5f5408b470a636f583bf74c0d7bbaf75d72
- https://github.com/smallstep/certificates
