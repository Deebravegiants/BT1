# [M] Cosign verification accepts any valid Rekor entry under certain conditions

## Summary
Severity: Medium
Advisory: GHSA-whqx-f9j3-ch6m
CVE: CVE-2026-22703
CWE: CWE-345
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-01-13
Source: https://github.com/advisories/GHSA-whqx-f9j3-ch6m
Type: github-advisory

## Affected
- Go: `github.com/sigstore/cosign/v3` — affected >=0 <3.0.4
- Go: `github.com/sigstore/cosign/v2` — affected >=0 <2.6.2

## Details
### Impact

A Cosign bundle can be crafted to successfully verify an artifact even if the embedded Rekor entry does not reference the artifact's digest, signature or public key. When verifying a Rekor entry, Cosign verifies the Rekor entry signature, and also compares the artifact's digest, the user's public key from either a Fulcio certificate or provided by the user, and the artifact signature to the Rekor entry contents. Without these comparisons, Cosign would accept any response from Rekor as valid. A malicious actor that has compromised a user's identity or signing key could construct a valid Cosign bundle by including any arbitrary Rekor entry, thus preventing the user from being able to audit the signing event.

This vulnerability only affects users that provide a trusted root via `--trusted-root` or when fetched automatically from a TUF repository, when no trusted key material is provided via `SIGSTORE_REKOR_PUBLIC_KEY`. When using the default flag values in Cosign v3 to sign and verify (`--use-signing-config=true` and `--new-bundle-format=true` for signing, `--new-bundle-format=true` for verification), users are unaffected. Cosign v2 users are affected using the default flag values.

This issue had previously been fixed in https://github.com/sigstore/cosign/security/advisories/GHSA-8gw7-4j42-w388 but recent refactoring caused a regression. We have added testing to prevent a future regression.

#### Steps to Reproduce

```
echo blob > /tmp/blob
cosign sign-blob -y --new-bundle-format=false --bundle /tmp/bundle.1 --use-signing-config=false /tmp/blob
cosign sign-blob -y --new-bundle-format=false --bundle /tmp/bundle.2 --use-signing-config=false /tmp/blob
jq ".rekorBundle |= $(jq .rekorBundle /tmp/bundle.2)" /tmp/bundle.1 > /tmp/bundle.3
cosign verify-blob --bundle /tmp/bundle.3 --certificate-identity-regexp='.*' --certificate-oidc-issuer-regexp='.*' /tmp/blob
```

### Patches

Upgrade to Cosign v2.6.2 or Cosign v3.0.4. This does not affect Cosign v1.

### Workarounds

You can provide trusted key material via a set of flags under certain conditions. The simplest fix is to upgrade to the latest Cosign v2 or v3 release.

Note that the example below works for `cosign verify`, `cosign verify-blob, `cosign verify-blob-attestation`, and `cosign verify-attestation`.

```
SIGSTORE_REKOR_PUBLIC_KEY=<path to Rekor pub key> cosign verify-blob --use-signing-config=false --new-bundle-format=false --bundle=<path to bundle> <artifact>
```

## References
- https://github.com/sigstore/cosign/security/advisories/GHSA-whqx-f9j3-ch6m
- https://nvd.nist.gov/vuln/detail/CVE-2026-22703
- https://github.com/sigstore/cosign/pull/4623
- https://github.com/sigstore/cosign/commit/6832fba4928c1ad69400235bbc41212de5006176
- https://github.com/sigstore/cosign
