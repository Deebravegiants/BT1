# [H] ZITADEL Account Takeover via Malicious Host Header Injection

## Summary
Severity: High
Advisory: GHSA-2wmj-46rj-qm2w
CVE: CVE-2023-49097
CWE: CWE-640
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2023-11-29
Source: https://github.com/advisories/GHSA-2wmj-46rj-qm2w
Type: github-advisory

## Affected
- Go: `github.com/zitadel/zitadel` — affected >=2.39.0 <2.39.9
- Go: `github.com/zitadel/zitadel` — affected >=2.40.0 <2.40.10
- Go: `github.com/zitadel/zitadel` — affected >=2.41.0 <2.41.6

## Details
### Impact

ZITADEL uses the notification triggering requests Forwarded or X-Forwarded-Host header to build the button link sent in emails for confirming a password reset with the emailed code. If this header is overwritten and a user clicks the link to a malicious site in the email, the secret code can be retrieved and used to reset the users password and take over his account.

Accounts with MFA or Passwordless enabled can not be taken over by this attack.

### Patches

The patched ZITADEL versions verify, that the auth requests instance is retrieved by the requests original domain (from the Forwarded or X-Forwarded-Host headers if available). If the instance can't be found using the original host or the auth request can't be found within that instance, ZITADEL throws an error.

2.x versions are fixed on >= [2.41.6](https://github.com/zitadel/zitadel/releases/tag/v2.41.6)
2.40.x versions are fixed on >= [2.40.10](https://github.com/zitadel/zitadel/releases/tag/v2.40.10)
2.39.x versions are fixed on >= [2.39.9](https://github.com/zitadel/zitadel/releases/tag/v2.39.9)

The vulnerablility was introduced with 2.39.0.

### Workarounds

A ZITADEL fronting proxy can be configured to delete all Forwarded and X-Forwarded-Host header values before sending requests to ZITADEL self-hosted environments.

### References

None

### Questions

If you have any questions or comments about this advisory, please email us at [security@zitadel.com](mailto:security@zitadel.com)

## References
- https://github.com/zitadel/zitadel/security/advisories/GHSA-2wmj-46rj-qm2w
- https://nvd.nist.gov/vuln/detail/CVE-2023-49097
- https://github.com/zitadel/zitadel
