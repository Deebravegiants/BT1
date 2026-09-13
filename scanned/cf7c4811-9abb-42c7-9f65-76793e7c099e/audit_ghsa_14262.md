# [H] Authentication Bypass in @strapi/plugin-users-permissions

## Summary
Severity: High
Advisory: GHSA-xv3q-jrmm-4fxv
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2023-04-18
Source: https://github.com/advisories/GHSA-xv3q-jrmm-4fxv
Type: github-advisory

## Affected
- npm: `@strapi/plugin-users-permissions` — affected >=3.2.1 <4.6.0

## Details
### Summary

Strapi through 4.5.6 does not verify the access or ID tokens issued during the OAuth flow when the AWS Cognito login provider is used for authentication.

### Details

Strapi through 4.5.6 does not verify the access or ID tokens issued during the OAuth flow when the AWS Cognito login provider is used for authentication. A remote attacker could forge an ID token that is signed using the 'None' type algorithm to bypass authentication and impersonate any user that use AWS Cognito for authentication.

### IoC

Reviewing of application logs is recommended to detect any suspicious activity. Running the following regex pattern will extract all ID tokens sent to `/api/auth/cognito/callback`.

`/\/api\/auth\/cognito\/callback\?[\s\S]*id_token=\s*([\S]*)/`

Once you have a list of the ID tokens, you will need to verify each token using the public key file for your AWS Cognito user pool that you can download from `https://cognito-idp.{region}.amazonaws.com/{userPoolId}/.well-known/jwks.json`. If there are any JWT tokens that cannot be verified using the correct public key, then you need to inspect the JWT body and see if it contains the `email` and `cognito:username` claims (example below).

```json
{
  "cognito:username": "auth-bypass-example",
  "email": "user@example.com"
}
```

If there are any JWTs that have this body, verify when the account with the email address was created. If the account was created earlier than the request to `/api/auth/cognito/callback` with the invalid JWT token, then you need to contact the user to inform them their account has been breached!

After upgrading to Strapi v4.6.0 or greater you will need to reconfigure your AWS Cognito provider to include the JWKS URL for it to work properly. If you do not reconfigure your provider you will receive an error message when attempting to login.


### Impact

Any Strapi user using the users-permissions AWS Cognito provider before 4.6.0

## References
- https://github.com/strapi/strapi/security/advisories/GHSA-xv3q-jrmm-4fxv
- https://github.com/strapi/strapi/pull/15382
- https://github.com/strapi/strapi/commit/d0edd25ceb49d275d710bf8d59999a2c07072893
- https://github.com/strapi/strapi
- https://github.com/strapi/strapi/releases/tag/v4.6.0
