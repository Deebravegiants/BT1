# [C] Dispatch writes JWT tokens in error message

## Summary
Severity: Critical
Advisory: CVE-2023-40171
Aliases: GHSA-fv3x-67q3-6pg7
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2023-08-17
Source: https://osv.dev/vulnerability/CVE-2023-40171
Type: osv

## Details
Dispatch is an open source security incident management tool. The server response includes the JWT Secret Key used for signing JWT tokens in error message when the `Dispatch Plugin - Basic Authentication Provider` plugin encounters an error when attempting to decode a JWT token. Any Dispatch users who own their instance and rely on the `Dispatch Plugin - Basic Authentication Provider` plugin for authentication may be impacted, allowing for any account to be taken over within their own instance. This could be done by using the secret to sign attacker crafted JWTs. If you think that you may be impacted, we strongly suggest you to rotate the secret stored in the `DISPATCH_JWT_SECRET` envvar in the `.env` file. This issue has been addressed in commit `b1942a4319` which has been included in the `20230817` release. users are advised to upgrade. There are no known workarounds for this vulnerability.

## References
- https://github.com/Netflix/dispatch/releases/tag/latest
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/40xxx/CVE-2023-40171.json
- https://github.com/Netflix/dispatch/security/advisories/GHSA-fv3x-67q3-6pg7
- https://nvd.nist.gov/vuln/detail/CVE-2023-40171
- https://github.com/Netflix/dispatch/commit/b1942a4319f0de820d86b84a58ebc85398b97c70
- https://github.com/Netflix/dispatch/pull/3695
