# [H] Appsmith: Configuration-dependent origin validation bypass in password reset and email verification link generation

## Summary
Severity: High
Advisory: GHSA-j9gf-vw2f-9hrw
CWE: CWE-346, CWE-807
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-06-12
Source: https://github.com/advisories/GHSA-j9gf-vw2f-9hrw
Type: github-advisory

## Affected
- Maven: `com.appsmith:server` — affected >=0 <2.0

## Details
### Summary
A configuration-dependent origin validation bypass was identified in Appsmith’s password reset and email verification flows on current `release`.

Both flows derive the email-link base URL from the request `Origin` header. The current validation only enforces a trusted base URL when `APPSMITH_BASE_URL` is configured. If that setting is unset, the application accepts the caller-supplied origin and uses it to generate token-bearing reset and verification links.

On deployments with email delivery enabled and `APPSMITH_BASE_URL` unset, this can cause Appsmith to send security-sensitive links whose clickable host is attacker-controlled, which can plausibly lead to account takeover after victim interaction.

### Details
The current `release` head at commit `e77639eca4974469c1e676904851ffdaedd38111` was reviewed.

The relevant routes are publicly reachable in `SecurityConfig.java`:

- `POST /forgotPassword` is permitted without authentication at line `209`
- `POST /resendEmailVerification` is permitted without authentication at line `228`

In `UserControllerCE.java`, both flows copy the request `Origin` header into the DTO field used as the email-link base URL:

- `forgotPasswordRequest(...)` at lines `91-94`
- `resendEmailVerification(...)` at lines `189-193`

In `UserServiceCEImpl.java`, base URL validation is conditional:

- `@Value("${APPSMITH_BASE_URL:}")` at line `113`
- `resolveSecureBaseUrl(...)` at lines `132-145`

That method explicitly documents and implements this behavior:

- if `APPSMITH_BASE_URL` is configured, the provided URL must match it
- if `APPSMITH_BASE_URL` is unset, the provided URL is accepted for backward compatibility

The resulting base URL is then used to construct token-bearing links:

- `FORGOT_PASSWORD_CLIENT_URL_FORMAT` at line `149`
- reset URL generation at lines `282-289`
- `EMAIL_VERIFICATION_CLIENT_URL_FORMAT` at line `152`
- verification URL generation at lines `931-940`

This means the base URL is not only used for branding or display purposes. It directly controls the clickable host of security-sensitive reset and verification links.

Note that the admin UI describes APPSMITH_BASE_URL as required for password reset and email verification links in:

- `app/client/src/ce/pages/AdminSettings/config/configuration.tsx` at lines `41-49`

The reviewed self-host material indicates this protection is not fail-closed by default, which makes the vulnerable condition realistic on existing deployments where operators have not set `APPSMITH_BASE_URL`.


### PoC
These steps were designed for validation on an Appsmith deployment that I own or am explicitly authorized to test.

1. Deploy a non-production Appsmith instance from current `release`, or any build containing the affected code.
2. Enable outbound email delivery.
3. Leave `APPSMITH_BASE_URL` unset or blank.
4. Use a test mailbox account you control, for example `victim@example.test`.
5. Send a password reset request with a forged `Origin` header:

```bash
curl -i -X POST 'https://YOUR-INSTANCE/api/v1/users/forgotPassword' \
  -H 'Content-Type: application/json' \
  -H 'Origin: https://attacker.example' \
  --data '{"email":"victim@example.test"}'
```

6. Inspect the delivered email. If affected, the clickable reset link is generated under `https://attacker.example/...` instead of the legitimate Appsmith host.
7. Repeat the same validation for resend email verification using an unverified test account:
```bash
curl -i -X POST 'https://YOUR-INSTANCE/api/v1/users/resendEmailVerification' \
  -H 'Content-Type: application/json' \
  -H 'Origin: https://attacker.example' \
  --data '{"email":"victim@example.test"}'
```

8. Inspect the delivered verification email. If affected, the clickable verification link is generated under `https://attacker.example/....`
9. Set `APPSMITH_BASE_URL=https://YOUR-INSTANCE`, restart the server, and repeat the same requests.
10. The expected secure behavior is that mismatched `Origin`  is rejected, or the generated links no longer follow the forged request header.

Live tokens, third-party data, or unsafe exploitation material was not included in this report. The attached archive contains source excerpts, data-flow proof, safe validation notes, and supporting evidence collected from the reviewed current branch.

### Impact
This is a trust-boundary failure in token-bearing email authentication flows.

Affected deployments are those where:

- `APPSMITH_BASE_URL` is unset or blank
- outbound email is enabled
- password reset and/or email verification flows are enabled

Attacker requirements are low:

- no prior authentication is required to reach the relevant endpoints
- the attacker only needs to trigger an email flow toward a target account

Security impact:

- Appsmith can generate password reset or verification emails whose clickable host is attacker-controlled
- victim interaction can expose security-sensitive token material
- this can plausibly result in account takeover
- at minimum, it enables trusted-email abuse and phishing through the application itself
 
### mitigation
1. Remove the fallback behavior in `resolveSecureBaseUrl(...)` that accepts caller-supplied origin data when `APPSMITH_BASE_URL` is unset.
2. Fail closed for all token-bearing email flows when no trusted base URL is configured.
3. Use a single trusted-base-url helper across:
   - password reset
   - resend email verification
   - invite flows
   - instance admin invite flows
4. Add regression tests for the unset-configuration case.
5. Add startup or admin-level validation so security-sensitive email flows cannot operate until a trusted base URL is configured.

### Attachment
[appsmith-email-link-origin-validation-bypass-20260321.zip](https://github.com/user-attachments/files/26153718/appsmith-email-link-origin-validation-bypass-20260321.zip)

## References
- https://github.com/appsmithorg/appsmith/security/advisories/GHSA-j9gf-vw2f-9hrw
- https://github.com/appsmithorg/appsmith
- https://github.com/appsmithorg/appsmith/releases/tag/v2.0
