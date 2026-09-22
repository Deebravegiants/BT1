# [M] The FIDO2/Webauthn Support for PHP library allows enumeration of valid usernames 

## Summary
Severity: Medium
Advisory: GHSA-875x-g8p7-5w27
CVE: CVE-2024-39912
CWE: CWE-204
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2024-07-15
Source: https://github.com/advisories/GHSA-875x-g8p7-5w27
Type: github-advisory

## Affected
- Packagist: `web-auth/webauthn-lib` — affected >=4.5.0 <4.9.0
- Packagist: `web-auth/webauthn-framework` — affected >=4.5.0 <4.9.0

## Details
### Summary

The ProfileBasedRequestOptionsBuilder method returns allowedCredentials without any credentials if no username was found.

### Details

When WebAuthn is used as the first or only authentication method, an attacker can enumerate usernames based on the absence of the `allowedCredentials` property in the assertion options response. This allows enumeration of valid or invalid usernames.

#### Proposal how to resolve it:
 
```
return $this->publicKeyCredentialRequestOptionsFactory->create(
            $this->profile,
            count($allowedCredentials) <= 0 ? self::getRandomCredentials(): $allowedCredentials,
            $optionsRequest->userVerification,
            $extensions
);

private static function getRandomCredentials(): array
{
        $credentialSources = [];
        for ($i = 0; $i <= rand(0,1); $i++) {
            $credentialSources[] = new PublicKeyCredentialSource(
                random_bytes(32),
                "public-key",
                [],
                "basic",
                new EmptyTrustPath(),
                Uuid::v7(),
                random_bytes(77),
                Uuid::v7()->__toString(),
                rand(0, 6000),
                null
            );
        }
        return array_map(
            static fn (PublicKeyCredentialSource $credential): PublicKeyCredentialDescriptor => $credential->getPublicKeyCredentialDescriptor(),
            $credentialSources
        );
}
```

### PoC

curl https://example.com/assertion/options \
  -H 'content-type: application/json' \
  --data-raw '{"username":"NotMeRandomUsername123"}'

### Impact

By knowing which usernames are valid, attackers can focus their efforts on a smaller set of potential targets, increasing the efficiency and likelihood of successful attacks.

## References
- https://github.com/web-auth/webauthn-framework/security/advisories/GHSA-875x-g8p7-5w27
- https://nvd.nist.gov/vuln/detail/CVE-2024-39912
- https://github.com/web-auth/webauthn-framework/commit/64de11f6cddc71e56c76e0cc4573bf94d02be045
- https://github.com/web-auth/webauthn-framework/commit/a9d1352897fba552e659e1445a771dec2d4ed05a
- https://github.com/web-auth/webauthn-lib/commit/b6798de27cdedd8681fe4c9b13ace0ff2456d18b
- https://github.com/web-auth/webauthn-framework
