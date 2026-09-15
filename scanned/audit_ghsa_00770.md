# [C] Incorrect persistent NameID generation in SimpleSAMLphp

## Summary
Severity: Critical
Advisory: GHSA-gp2m-7cfp-h6gf
CVE: CVE-2017-12873
CWE: CWE-384
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2020-01-24
Source: https://github.com/advisories/GHSA-gp2m-7cfp-h6gf
Type: github-advisory

## Affected
- Packagist: `simplesamlphp/simplesamlphp` — affected >=1.7.0 <1.14.11

## Details
### Background
When a SimpleSAMLphp Identity Provider is misconfigured, a bug in the software when trying to build a persistent `NameID` to univocally identify the authenticating subject could cause different users to get the same identifier generated, depending on the attributes available for them right after authentication.

Please note that even though this is possible thanks to a bug, **an IdP must be misconfigured** to release persistent `NameID`s even if it is not properly configured to generate them based on the specifics of the deployment.

### Description
Persistent `NameID`s will typically be sent as part of the `Subject` element of a SAML assertion, or as the contents of the `eduPersonTargetedID` attribute. Here is an example of such a `NameID`:

    <NameID Format=“urn:oasis:names:tc:SAML:2.0:nameid-format:persistent“>
        zbonsm0Yn9Gnw14uQEEPr6AO7d+IvxwCQN3t+o24jYs=
    </NameID>

Some service providers will use this information to identify a user across sessions because a persistent `NameID` will never change for a given user. This could lead to different users accessing the same account in those service providers.

In order to be affected by this issue, the following circumstances must concur:

- SimpleSAMLphp acts as an identity provider.
- The service provider asking for authentication requests a persistent `NameID`.
- No `saml:PersistentNameID` authentication processing filter is configured (neither for the whole IdP, nor for a given SP).
- No `simplesaml.nameidattribute` configuration option is set (neither for the whole IdP, nor for a given SP).
- One of the following alternatives:
  - No `userid.attribute` configuration option is set **and** the users don't have an `eduPersonPrincipalName` attribute in the users backend, **or**
  - the `userid.attribute` configuration option is set to an empty or missing attribute.

If all these requirements are met, the `SimpleSAML_Auth_ProcessingChain` class will try to keep a unique user identifier in the state array (`addUserID()` method). Bear in mind that this code is executed **before** all the authentication processing filters configured, meaning that only those attributes retrieved for the user during **initial authentication** will be available. If no `userid.attribute` configuration option is set, the default `eduPersonPrincipalName` will then be used. However, since it is missing, no identifier will be kept. Alternatively, if `userid.attribute` is set to a missing or empty attribute, the `addUserID()` method will abort trying to register an identifier.

After executing all authentication processing filters, SimpleSAMLphp will build a SAML assertion. If the service provider requests persistent `NameID`s, SimpleSAMLphp will attempt to generate one given that none is already available (because the `saml:PersistentNameID` filter was not used). At this point, the code will look for the `simplesaml.nameidattribute` configuration option in either the local IdP metadata or in the remote SP metadata. If none of them are configured, it will default to the unique user identifier previously registered by `SimpleSAML_Auth_ProcessingChain`. If no identifier was kept there, the code will log an error message:

    Unable to generate NameID. Check the userid.attribute option.

However, instead of aborting the `NameID` generation at that point, it will go on and use a value missing from the state array as the source for the computation, meaning the `null` type will be used. Hence, all users connecting to a given service provider will get the same `NameID` generated, because all the input parameters will be the same:

- The SP's entity identifier.
- The IdP's entity identifier.
- The `null` value.
- The common secret salt from the main configuration.

### Affected versions
All SimpleSAMLphp versions between 1.7.0 and 1.14.10, inclusive.

### Impact
Those identity providers affected by this bug and misconfigured as previously described could be issuing SAML assertions with common `NameID`s for all or a subset of their users. If a service provider uses those `NameID`s to identify the users of the affected IdP, all the users will be associated with the same user account at the service provider, causing all sorts of potential security issues like information disclosure or unauthorized access.

While we can consider this unlikely to happen, some cases have been already observed. In particular, some identity providers using default configurations and consuming metadata automatically (i.e. using the _metarefresh_ module) while using a user backend like _Active Directory_ that does not populate `eduPersonPrincipalName` are particularly sensitive to this issue.

### Resolution
Upgrade to the latest version.

Configure a `saml:PersistentNameID` authentication processing filter according to your needs. Remember to check that **the attribute used as the source** for the `NameID` **is present at the moment the `saml:PersistentNameID` filter is executed**. The attribute used must be **unique** per user, and **must not change** over time.

## References
- https://github.com/simplesamlphp/simplesamlphp/security/advisories/GHSA-gp2m-7cfp-h6gf
- https://nvd.nist.gov/vuln/detail/CVE-2017-12873
- https://github.com/simplesamlphp/simplesamlphp/commit/90dca835158495b173808273e7df127303b8b953
- https://github.com/FriendsOfPHP/security-advisories/blob/master/simplesamlphp/simplesamlphp/CVE-2017-12873.yaml
- https://lists.debian.org/debian-lts-announce/2017/12/msg00007.html
- https://simplesamlphp.org/security/201612-04
- https://www.debian.org/security/2018/dsa-4127
