# [M] io.micronaut.security:micronaut-security-oauth2 has invalid IdTokenClaimsValidator logic on aud

## Summary
Severity: Medium
Advisory: GHSA-qw22-8w9r-864h
CVE: CVE-2023-36820
CWE: CWE-284
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2023-10-05
Source: https://github.com/advisories/GHSA-qw22-8w9r-864h
Type: github-advisory

## Affected
- Maven: `io.micronaut.security:micronaut-security-oauth2` — affected >=3.11.0 <3.11.1
- Maven: `io.micronaut.security:micronaut-security-oauth2` — affected >=3.10.0 <3.10.2
- Maven: `io.micronaut.security:micronaut-security-oauth2` — affected >=3.9.0 <3.9.6
- Maven: `io.micronaut.security:micronaut-security-oauth2` — affected >=3.8.0 <3.8.4
- Maven: `io.micronaut.security:micronaut-security-oauth2` — affected >=3.7.0 <3.7.4
- Maven: `io.micronaut.security:micronaut-security-oauth2` — affected >=3.6.0 <3.6.6
- Maven: `io.micronaut.security:micronaut-security-oauth2` — affected >=3.5.0 <3.5.3
- Maven: `io.micronaut.security:micronaut-security-oauth2` — affected >=3.4.0 <3.4.3
- Maven: `io.micronaut.security:micronaut-security-oauth2` — affected >=3.3.0 <3.3.2
- Maven: `io.micronaut.security:micronaut-security-oauth2` — affected >=3.2.0 <3.2.4
- Maven: `io.micronaut.security:micronaut-security-oauth2` — affected >=3.1.0 <3.1.2

## Details
### Summary

IdTokenClaimsValidator skips `aud` claim validation if token is issued by same identity issuer/provider.

### Details

See https://github.com/micronaut-projects/micronaut-security/blob/master/security-oauth2/src/main/java/io/micronaut/security/oauth2/client/IdTokenClaimsValidator.java#L202

This logic violates point 3 of https://openid.net/specs/openid-connect-core-1_0.html#IDTokenValidation. 

Workaround exists by setting `micronaut.security.token.jwt.claims-validators.audience` with valid values. 
 `micronaut.security.token.jwt.claims-validators.openid-idtoken` can be kept as default on.

### PoC

Should probably be:

```java
                return issuer.equalsIgnoreCase(iss) &&
                        audiences.contains(clientId) &&
                                validateAzp(claims, clientId, audiences);
```

### Impact

Any OIDC setup using Micronaut where multiple OIDC applications exists for the same issuer but token auth are not meant to be shared.


### Mitigation

Please upgrade to a patched `micronaut-security-oauth2` release as soon as possible.  

If you cannot upgrade, for example, if you are still using Micronaut Framework 2, you can patch your application by creating a replacement of `IdTokenClaimsValidatorReplacement`

```java
package cve;

import io.micronaut.context.annotation.Replaces;
import io.micronaut.context.annotation.Requires;
import io.micronaut.core.annotation.NonNull;
import io.micronaut.core.util.StringUtils;
import io.micronaut.security.config.SecurityConfigurationProperties;
import io.micronaut.security.oauth2.client.IdTokenClaimsValidator;
import io.micronaut.security.oauth2.configuration.OauthClientConfiguration;
import io.micronaut.security.oauth2.configuration.OpenIdClientConfiguration;
import io.micronaut.security.token.jwt.generator.claims.JwtClaims;
import io.micronaut.security.token.jwt.validator.JwtClaimsValidatorConfigurationProperties;

import javax.inject.Singleton;
import java.net.URL;
import java.util.Collection;
import java.util.List;
import java.util.Optional;

@Requires(property = SecurityConfigurationProperties.PREFIX + ".authentication", value = "idtoken")
@Requires(property = JwtClaimsValidatorConfigurationProperties.PREFIX + ".openid-idtoken", notEquals = StringUtils.FALSE)
@Singleton
@Replaces(IdTokenClaimsValidator.class)
public class IdTokenClaimsValidatorReplacement extends IdTokenClaimsValidator {
    public IdTokenClaimsValidatorReplacement(Collection<OauthClientConfiguration> oauthClientConfigurations) {
        super(oauthClientConfigurations);
    }

    @Override
    protected boolean validateIssuerAudienceAndAzp(@NonNull JwtClaims claims,
                                                   @NonNull String iss,
                                                   @NonNull List<String> audiences,
                                                   @NonNull String clientId,
                                                   @NonNull OpenIdClientConfiguration openIdClientConfiguration) {
        if (openIdClientConfiguration.getIssuer().isPresent()) {
            Optional<URL> issuerOptional = openIdClientConfiguration.getIssuer();
            if (issuerOptional.isPresent()) {
                String issuer = issuerOptional.get().toString();
                return issuer.equalsIgnoreCase(iss) &&
                        audiences.contains(clientId) &&
                                validateAzp(claims, clientId, audiences);
            }
        }
        return false;
    }
}
``

## References
- https://github.com/micronaut-projects/micronaut-security/security/advisories/GHSA-qw22-8w9r-864h
- https://nvd.nist.gov/vuln/detail/CVE-2023-36820
- https://github.com/micronaut-projects/micronaut-security/commit/9728b925221a0d87798ccf250657a3c214b7e980
- https://github.com/micronaut-projects/micronaut-security
- https://github.com/micronaut-projects/micronaut-security/blob/master/security-oauth2/src/main/java/io/micronaut/security/oauth2/client/IdTokenClaimsValidator.java#L202
