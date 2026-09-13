# [M] DiceBear: SVG injection via the unescaped rotate option in @dicebear/core (and fontSize/fontWeight in @dicebear/initials)

## Summary
Severity: Medium
Advisory: CVE-2026-68921
Aliases: GHSA-gcr2-9v8m-gq45
CVSS: 4.7 (CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:C/C:L/I:L/A:N)
Published: 2026-08-20
Source: https://osv.dev/vulnerability/CVE-2026-68921
Type: osv

## Details
DiceBear is an avatar library for designers and developers. Prior to 9.4.3, @dicebear/core interpolates the rotate option into an SVG transform attribute without XML escaping in addRotate in packages/@dicebear/core/src/utils/svg.ts, while @dicebear/initials similarly emits fontSize and fontWeight without escaping in packages/@dicebear/initials/src/index.ts. Runtime callers can pass strings despite the numeric TypeScript types, break out of the attributes, and inject arbitrary SVG markup. Script can execute in the page origin when the generated avatar is inserted inline or served as image/svg+xml and opened directly, although exploitation requires an application to pass untrusted values into these normally developer-controlled options. This issue is fixed in @dicebear/core and @dicebear/initials version 9.4.3.

## References
- https://github.com/dicebear/dicebear/releases/tag/v9.4.3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68921.json
- https://github.com/dicebear/dicebear/security/advisories/GHSA-gcr2-9v8m-gq45
- https://nvd.nist.gov/vuln/detail/CVE-2026-68921
- https://github.com/dicebear/dicebear/commit/922946d738c4e77ab6c412e27ede75941fec4b59
