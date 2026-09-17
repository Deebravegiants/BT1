# [M] WPGraphQL has deprecated `user` field on SendPasswordResetEmailPayload that leaks user existence + profile (defeats explicit anti-enumeration design)

## Summary
Severity: Medium
Advisory: GHSA-jhh7-832h-f8hv
CVE: CVE-2026-54768
CWE: CWE-204
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-31
Source: https://github.com/advisories/GHSA-jhh7-832h-f8hv
Type: github-advisory

## Affected
- Packagist: `wp-graphql/wp-graphql` — affected >=0

## Details
## Summary

The `sendPasswordResetEmail` mutation in WPGraphQL is explicitly designed to prevent user enumeration. The resolver in `src/Mutation/SendPasswordResetEmail.php` states in a code comment:

`// We obsfucate the actual success of this mutation to prevent user enumeration.`

The mutation always returns `success: true` regardless of whether the supplied username/email belongs to an existing user. The intended public output field is only `success: Boolean`.

However, a deprecated `user` field is still registered on the `SendPasswordResetEmailPayload` output type in `src/Deprecated.php` (lines 433-450). This deprecated field resolves to a full `User` object when the supplied username/email corresponds to an existing author-class user, and `null` otherwise — completely undermining the anti-enumeration design.

The `@todo remove in 3.0.0` comment acknowledges the field is scheduled for removal, but it remains active in all 2.x releases, including current 2.14.1.

Discovered via source code review on May 29, 2026.

## Details

The mutation resolver in `src/Mutation/SendPasswordResetEmail.php`:

```php
$payload = ['success' => true, 'id' => null];
$user_data = self::get_user_data($input['username']);
if (!$user_data) {
    graphql_debug(...);
    return $payload;  // id stays null
}
// ...send email, then...
return ['id' => $user_data->ID, 'success' => true];
```

The intended public output field is only `success`. The `id` is internal-only state for downstream resolvers.

`src/Deprecated.php` registers an additional `user` field on the same payload type:

```php
register_graphql_field(
    'SendPasswordResetEmailPayload',
    'user',
    [
        'type' => 'User',
        'deprecationReason' => static function () { return __('This field will be removed...'); },
        'resolve' => static function ($payload, $args, AppContext $context) {
            return !empty($payload['id'])
                ? $context->get_loader('user')->load_deferred($payload['id'])
                : null;
        },
    ],
);
```

This field reads the internal `$payload['id']` and resolves it through the standard user loader. The User Model's `allowed_restricted_fields` policy permits unauthenticated reads of public author fields (`databaseId`, `name`, `firstName`, `lastName`, `slug`, `description`, `uri`, `url`).

## PoC

```graphql
mutation EnumerateUser {
  sendPasswordResetEmail(input: { username: "victim@example.com" }) {
    success
    user {
      databaseId
      name
      firstName
      lastName
      slug
      description
      uri
    }
  }
}
```

Behavior:
- Non-existing user/email → `data.sendPasswordResetEmail.user` is `null`
- - Existing author-class user → `data.sendPasswordResetEmail.user` is a full User object with the listed fields populated
- - `success` always returns `true`, preserving the appearance of obfuscation — the deprecated `user` field is the leak
## Impact

1. **Username/email enumeration:** unauthenticated attacker can verify whether any username or email is registered, with no WPGraphQL-side rate limiting
2. 2. **Profile disclosure for author-class users:** for any user with published posts (including editors and administrators), the attacker obtains `databaseId`, `name`, `firstName`, `lastName`, `slug`, `description` (user bio), `uri` — substantially more than mere existence
3. 3. **Bypasses partial hardening:** sites that disabled the REST API user endpoint, the user XML sitemap, and `?author=N` author redirects may still be vulnerable through this WPGraphQL path
4. 4. **Spearphishing setup:** firstName/lastName/description for authors provides personalized phishing material
## Recommended fix

Either remove the deprecated `user` field entirely (advance the existing `@todo remove in 3.0.0`) or change the resolver to always return `null`:

```diff
'resolve' => static function ($payload, $args, AppContext $context) {
-    return !empty($payload['id']) ? $context->get_loader('user')->load_deferred($payload['id']) : null;
- +    // Always null — this deprecated field previously leaked user existence,
- +    // undermining the anti-enumeration design of the sendPasswordResetEmail mutation.
- +    return null;
- },
- ```
Defense in depth — change the mutation resolver itself to not populate `$payload['id']` on real success:

```diff
return [
-    'id'      => $user_data->ID,
- +    'id'      => null,
-      'success' => true,
- ];
- ```

Luke Granto — independent security researcher operating in good faith. Discovery via source code review of wp-graphql/wp-graphql v2.14.1, approximately 15 minutes from `git clone` to confirmed bug. No live exploitation against any third-party deployment.

## References
- https://github.com/wp-graphql/wp-graphql/security/advisories/GHSA-jhh7-832h-f8hv
- https://github.com/wp-graphql/wp-graphql
- https://github.com/wp-graphql/wp-graphql/releases/tag/wp-graphql/v2.15.1
