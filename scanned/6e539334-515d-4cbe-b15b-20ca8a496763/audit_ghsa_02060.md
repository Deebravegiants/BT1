# [H] Auto-merging Person Records Compromised

## Summary
Severity: High
Advisory: GHSA-r578-pj6f-r4ff
CVE: CVE-2021-32691
CWE: CWE-287, CWE-303
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-06-21
Source: https://github.com/advisories/GHSA-r578-pj6f-r4ff
Type: github-advisory

## Affected
- npm: `@apollosproject/data-connector-rock` — affected >=0 <2.20.0

## Details
### Impact

New user registrations are able to access anyone's account by only knowing their basic profile information (name, birthday, gender, etc). This includes all app functionality within the app, as well as any authenticated links to Rock-based webpages (such as giving and events).

### Patches

We have released a security patch on v2.20.0. The solution was to create a duplicate person and then patch the new person with their profile details.

### Workarounds

If you do not wish to upgrade your app to the new version, you can patch your server by overriding the `create` data source method on the `People` class.

```js
  create = async (profile) => {
    const rockUpdateFields = this.mapApollosFieldsToRock(profile);
    // auto-merge functionality is compromised
    // we are creating a new user and patching them with profile details
    const id = await this.post('/People', {
      Gender: 0, // required by Rock. Listed first so it can be overridden.
      IsSystem: false, // required by rock
    });
    await this.patch(`/People/${id}`, {
      ...rockUpdateFields,
    });
    return id;
  };
```

### For more information
If you have any questions or comments about this advisory:
* Email us at [support@apollos.app](mailto:support@apollos.app)

## References
- https://github.com/ApollosProject/apollos-apps/security/advisories/GHSA-r578-pj6f-r4ff
- https://nvd.nist.gov/vuln/detail/CVE-2021-32691
- https://github.com/ApollosProject/apollos-apps/commit/cb5f8f1c0b24f1b215b2bb5eb6f9a8e16d728ce2
- https://github.com/ApollosProject/apollos-apps/releases/tag/v2.20.0
