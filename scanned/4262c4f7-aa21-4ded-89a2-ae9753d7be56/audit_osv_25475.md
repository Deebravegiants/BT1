# [C] CC: Tweaked SSRF to Cloud Services Metadata Services not Blocked by Default

## Summary
Severity: Critical
Advisory: CVE-2023-37262
CVSS: 9.6 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:N)
Published: 2023-07-07
Source: https://osv.dev/vulnerability/CVE-2023-37262
Type: osv

## Details
CC: Tweaked is a mod for Minecraft which adds programmable computers, turtles, and more to the game. Prior to versions 1.20.1-1.106.0, 1.19.4-1.106.0, 1.19.2-1.101.3, 1.18.2-1.101.3, and 1.16.5-1.101.3, if the cc-tweaked plugin is running on a Minecraft server hosted on a popular cloud hosting providers, like AWS, GCP, and Azure, those metadata services API endpoints are not forbidden (aka "blacklisted") by default. As such, any player can gain access to sensitive information exposed via those metadata servers, potentially allowing them to pivot or privilege escalate into the hosting provider. Versions 1.20.1-1.106.0, 1.19.4-1.106.0, 1.19.2-1.101.3, 1.18.2-1.101.3, and 1.16.5-1.101.3 contain a fix for this issue.

## References
- https://github.com/cc-tweaked/CC-Tweaked/blob/96847bb8c28df51e5e49f2dd2978ff6cc4e2821b/projects/core/src/main/java/dan200/computercraft/core/apis/http/options/AddressPredicate.java#L116-L126
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/37xxx/CVE-2023-37262.json
- https://github.com/MightyPirates/OpenComputers/security/advisories/GHSA-vvfj-xh7c-j2cm
- https://github.com/cc-tweaked/CC-Tweaked/security/advisories/GHSA-7p4w-mv69-2wm2
- https://nvd.nist.gov/vuln/detail/CVE-2023-37262
- https://github.com/dan200/ComputerCraft/issues/170
- https://github.com/cc-tweaked/CC-Tweaked/commit/4bbde8c50c00bc572578ab2cff609b3443d10ddf
