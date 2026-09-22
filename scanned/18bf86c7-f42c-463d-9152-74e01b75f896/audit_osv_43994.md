# [M] jackson-databind: Eager DNS resolution (SSRF) still present in InetAddress deserialization (Incomplete fix for CVE-2026-54514)

## Summary
Severity: Medium
Advisory: CVE-2026-77310
Aliases: GHSA-vvgp-rfg2-7rr6
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2026-08-24
Source: https://osv.dev/vulnerability/CVE-2026-77310
Type: osv

## Details
jackson-databind contains the general-purpose data-binding functionality and tree-model for Jackson Data Processor. Prior to versions 2.18.9, 2.21.5, 2.22.1, 3.1.5, and 3.2.1 on their respective release lines, the java.net.InetAddress branch of FromStringDeserializer.Std._deserialize() calls InetAddress.getByName() on attacker-controlled input, causing eager DNS resolution during deserialization and enabling DNS-based server-side request forgery and internal-host enumeration. This issue is fixed in versions 2.18.9, 2.21.5, 2.22.1, 3.1.5, and 3.2.1.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/77xxx/CVE-2026-77310.json
- https://github.com/FasterXML/jackson-databind/security/advisories/GHSA-vvgp-rfg2-7rr6
- https://nvd.nist.gov/vuln/detail/CVE-2026-77310
