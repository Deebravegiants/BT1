# [H] OpenSignLabs opensignserver - Broken Object Level Authorization

## Summary
Severity: High
Advisory: CVE-2026-72689
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-72689
Type: osv

## Details
A broken object-level authorization vulnerability in OpenSignLabs opensignserver through 2.37.0 allows an unauthenticated remote attacker to read complete contract records via the getDocument Parse cloud function. The function fetches documents using useMasterKey, bypassing the object ACL, and returns full records including sender and signer PII and a pre-signed document download URL whenever the document's IsEnableOTP flag is unset, which is the default configuration.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72689.json
- https://github.com/OpenSignLabs/OpenSign
- https://nvd.nist.gov/vuln/detail/CVE-2026-72689
