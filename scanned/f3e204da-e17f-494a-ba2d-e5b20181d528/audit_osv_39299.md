# [H] CubeCart: Pre-Authenticated Password Reset Link Poisoning via HTTP Host Header

## Summary
Severity: High
Advisory: CVE-2026-45055
Aliases: GHSA-7pvc-gxc4-chmc
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:N)
Published: 2026-05-13
Source: https://osv.dev/vulnerability/CVE-2026-45055
Type: osv

## Details
CubeCart is an ecommerce software solution. Prior to 6.7.2, CubeCart 6.6.x – 6.7.1 builds CC_STORE_URL directly from the Host request header at bootstrap, with no allowlist. The constant is embedded verbatim into transactional email links, most critically the password-reset link in User::passwordRequest() (and the admin equivalent in Admin::passwordRequest()). An unauthenticated attacker who knows a target email can POST /index.php?_a=recover with Host: evil.com; CubeCart writes a fresh verify token (valid 3,600 s) and emails the victim a link http://evil.com/index.php?_a=recovery&validate=<TOKEN>. The token is valid against the legitimate store — capturing the victim's click on evil.com yields full account takeover, or store takeover when an admin email is targeted. This vulnerability is fixed in 6.7.2.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45055.json
- https://github.com/cubecart/v6/security/advisories/GHSA-7pvc-gxc4-chmc
- https://nvd.nist.gov/vuln/detail/CVE-2026-45055
