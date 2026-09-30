# [C] Misskey vulnerable to improper authorization when accessing with third-party application

## Summary
Severity: Critical
Advisory: CVE-2023-52139
Aliases: GHSA-7pxq-6xx9-xpgm
CVSS: 9.0 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:H/A:H)
Published: 2023-12-29
Source: https://osv.dev/vulnerability/CVE-2023-52139
Type: osv

## Details
Misskey is an open source, decentralized social media platform. Third-party applications may be able to access some endpoints or Websocket APIs that are incorrectly specified as [kind](https://github.com/misskey-dev/misskey/blob/406b4bdbe79b5b0b68fcdcb3c4b6e419460a0258/packages/backend/src/server/api/endpoints.ts#L811) or [secure](https://github.com/misskey-dev/misskey/blob/406b4bdbe79b5b0b68fcdcb3c4b6e419460a0258/packages/backend/src/server/api/endpoints.ts#L805) without the user's permission and perform operations such as reading or adding non-public content. As a result, if the user who authenticated the application is an administrator, confidential information such as object storage secret keys and SMTP server passwords will be leaked, and general users can also create invitation codes without permission and leak non-public user information. This is patched in version [2023.12.1](https://github.com/misskey-dev/misskey/commit/c96bc36fedc804dc840ea791a9355d7df0748e64).

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52139.json
- https://github.com/misskey-dev/misskey/security/advisories/GHSA-7pxq-6xx9-xpgm
- https://nvd.nist.gov/vuln/detail/CVE-2023-52139
- https://github.com/misskey-dev/misskey/commit/c96bc36fedc804dc840ea791a9355d7df0748e64
