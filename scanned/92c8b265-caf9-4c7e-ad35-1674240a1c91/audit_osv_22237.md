# [H] CVE-2022-23949

## Summary
Severity: High
Advisory: CVE-2022-23949
Aliases: GHSA-87gh-qc28-j9mm
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2022-09-21
Source: https://osv.dev/vulnerability/CVE-2022-23949
Type: osv

## Details
In Keylime before 6.3.0, unsanitized UUIDs can be passed by a rogue agent and can lead to log spoofing on the verifier and registrar.

## References
- https://seclists.org/oss-sec/2022/q1/101
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/23xxx/CVE-2022-23949.json
- https://github.com/keylime/keylime/security/advisories/GHSA-87gh-qc28-j9mm
- https://nvd.nist.gov/vuln/detail/CVE-2022-23949
- https://github.com/keylime/keylime/commit/387e320dc22c89f4f47c68cb37eb9eec2137f34b
- https://github.com/keylime/keylime/commit/65c2b737129b5837f4a03660aeb1191ced275a57
- https://github.com/keylime/keylime/commit/e429e95329fc60608713ddfb82f4a92ee3b3d2d9
