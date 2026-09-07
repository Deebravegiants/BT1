# [M] Craft CMS Allows TOTP Token To Stay Valid After Use

## Summary
Severity: Medium
Advisory: GHSA-wmx7-pw49-88jx
CVE: CVE-2024-41800
CWE: CWE-287
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2024-07-25
Source: https://github.com/advisories/GHSA-wmx7-pw49-88jx
Type: github-advisory

## Affected
- Packagist: `craftcms/cms` — affected >=5.0.0-beta.1 <5.2.3

## Details
Craft CMS 5 allows reuse of TOTP tokens multiple times within the validity period.

### Impact

An attacker is able to re-submit a valid TOTP token to establish an authenticated session. This requires that the attacker has knowledge of the victim's credentials.

A TOTP token can be used multiple times to establish an authenticated session.
[RFC 6238](https://www.rfc-editor.org/rfc/rfc6238) insists that an OTP must not be used more than once.

> The verifier MUST NOT accept the second attempt of the OTP after the successful validation has been issued for the first OTP, which ensures one-time only use of an OTP.

The OWASP Application Security Verification Standard v4.0.3 (ASVS) [reiterates
this property with requirement 2.8.4](https://github.com/OWASP/ASVS/blob/v4.0.3/4.0/en/0x11-V2-Authentication.md#v28-one-time-verifier).

> Verify that time-based OTP can be used only once within the validity period.

It should also be noted that the validity period of an TOTP token is 2 minutes. This makes a successful brute force attack more likely, since the four tokens are valid at the same time.

### Patches

This has been patched in Craft 5.2.3.

References:

https://github.com/sbaresearch/advisories/tree/public/2024/SBA-ADV 2024061701_CraftCMS_TOTP_Valid_After_Use

https://github.com/craftcms/cms/releases/tag/5.2.3

## References
- https://github.com/craftcms/cms/security/advisories/GHSA-wmx7-pw49-88jx
- https://nvd.nist.gov/vuln/detail/CVE-2024-41800
- https://github.com/craftcms/cms/commit/7c790fa5ad5a8cb8016cb6793ec3554c4c079e38
- https://github.com/craftcms/cms
- https://github.com/craftcms/cms/releases/tag/5.2.3
- https://github.com/sbaresearch/advisories/tree/public/2024/SBA-ADV-20240617-01_CraftCMS_TOTP_Valid_After_Use
