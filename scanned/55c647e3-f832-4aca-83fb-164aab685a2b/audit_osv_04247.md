# [H] authentik: Authentication Flow Bypass via Unguarded challenge_valid() in AuthenticatorEndpointGDTCStage and GoogleChromeStageView

## Summary
Severity: High
Advisory: BIT-authentik-2026-54730
Aliases: CVE-2026-54730, GHSA-3v9h-3hrm-29cx
Ecosystem: Bitnami
Published: 2026-08-24
Source: https://osv.dev/vulnerability/BIT-authentik-2026-54730
Type: osv

## Affected
- Bitnami: `authentik` — affected >=2026.5.0 <2026.5.5

## Details
authentik is an open-source identity provider. Prior to 2026.2.6 and 2026.5.5, the enterprise Google Chrome device-trust stages advance the flow without confirming that the out-of-band device attestation actually ran. Affected enterprise deployments place either a Google Chrome Endpoint stage with mode set to REQUIRED or the deprecated Google Chrome Device Trust Connector stage in an authentication flow. The device attestation occurs in a verification iframe that calls the Google Verified Access API and records the verified device on success, but the vulnerable stages treat the flow as passed as soon as the stage is submitted. An attacker who can reach such a stage, including after primary username and password authentication, can skip the verification iframe and authenticate from a device that was never verified. Where device trust is the only additional factor, that protection is fully bypassed, while other configured factors remain in force. This issue is fixed in versions 2026.2.6 and 2026.5.5.

## References
- https://github.com/goauthentik/authentik/commit/27866a94f29d0d7f784b3c462a697a968d3f6b9c
- https://github.com/goauthentik/authentik/commit/85adb0bbbd7ad4f2807ec21cf25bb42aee81afbc
- https://github.com/goauthentik/authentik/pull/24053
- https://github.com/goauthentik/authentik/pull/24058
- https://github.com/goauthentik/authentik/releases/tag/version/2026.2.6
- https://github.com/goauthentik/authentik/releases/tag/version/2026.5.5
- https://github.com/goauthentik/authentik/security/advisories/GHSA-3v9h-3hrm-29cx
- https://nvd.nist.gov/vuln/detail/CVE-2026-54730
