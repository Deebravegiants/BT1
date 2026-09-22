# [H] Craft CMS has IDOR via GraphQL @parseRefs

## Summary
Severity: High
Advisory: GHSA-7x43-mpfg-r9wj
CVE: CVE-2026-28696
CWE: CWE-639, CWE-862
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-03
Source: https://github.com/advisories/GHSA-7x43-mpfg-r9wj
Type: github-advisory

## Affected
- Packagist: `craftcms/cms` — affected >=4.0.0-RC1 <4.17.0-beta.1
- Packagist: `craftcms/cms` — affected >=5.0.0-RC1 <5.9.0-beta.1

## Details
The GraphQL directive `@parseRefs`, intended to parse internal reference tags (e.g., `{user:1:email}`), can be abused by both authenticated users and unauthenticated guests (if a Public Schema is enabled) to access sensitive attributes of any element in the CMS. The implementation in `Elements::parseRefs` fails to perform authorization checks, allowing attackers to read data they are not authorized to view.

## Vulnerability Details

`craft\services\Elements::parseRefs` identifies reference tags and resolves them using `_getRefTokenReplacement`. This method fetches the referenced element and accesses the specified attribute via $element->$attribute.

- Missing Auth Check: It bypasses `canView()` checks.
- Polymorphic Access: `getElementTypeByRefHandle` allows referencing any element type (entry, asset, user, category).
- Custom Field Access: Since Craft elements use `__get()` to resolve custom field handles, an attacker is not limited to core attributes. They can exfiltrate any custom field data by enumerating the field handle (e.g. `{entry:123:privateNotes}`).

## Attack Vectors

1. Privilege Escalation / User Data Leak

An attacker can enumerate sensitive attributes of administrators or other users.

- Payload: `{user:1:email}` or `{user:1:photoId}`

2. Arbitrary Property Reflection & Server-Side Logic Execution

The vulnerability allows reflecting any accessible property of the underlying Element model.

- Username/Admin Enumeration: `{user:1:username}` (Confirmed: returns admin), {user:1:admin}.
- Internal Path Disclosure: Accessing methods that trigger errors (e.g., `{user:1:authKey}`) exposes full server stack traces in the GraphQL error response (e.g., Exception: No user session token exists with paths like `/var/www/html/...`).

3. IDOR on Private Entries & Assets (Polymorphism)

The vulnerability is not limited to Users. Reference tags can target any element type.

- Payload: `{entry:456:myConfidentialField}` (Bypasses canView checks).
- Asset Path Leakage: `{volume:1:path}` can expose internal file system paths.

4. Unauthenticated Exploitation (Public Schema)

Confirmed locally. The `@parseRefs` directive is active in the Public Schema. By injecting a payload into a public-facing field (e.g., a "News" entry title), an unauthenticated guest can trigger the resolution and retrieve the sensitive output.

## Steps to Reproduce

1. Setup (Admin Panel):
- Create a Section (e.g., "News") and an Entry Type.
- Create a new Entry in that section. Set the Title to the payload: {user:1:username} or {user:1:email}.
- Go to GraphQL > Schemas > Public Schema. Enable it, and ensure "Query for elements in the Site" and "News" section queries are checked.

2. Execute Exploit (Unauthenticated):
- Send a POST request to http://localhost:8000/index.php?action=graphql/api:
```
curl -X POST \
-H "Content-Type: application/json" \
-d '{"query": "{ entries { title @parseRefs } }"}'
```

3. Observation:
- The API returns `{"data":{"entries":[{"title":"admin"}]}}` (or the email).
- Using `{user:1:authKey}` triggers an internal server error that leaks the full server path in string format.

## Impact

- Critical Information Disclosure: Full PII enumeration (emails, usernames).
- System Information Leakage: Absolute server paths via stack traces.
- Authentication Bypass: Guest accounts can effectively query the database as the system user.

## Recommended Fix

Modify `Elements::parseRefs` to enforce `canView` permissions on the resolved element before extracting attributes.

## References

https://github.com/craftcms/cms/commit/4d98a07e47580f1712095825d3e3c4d67bc9f8b9

## References
- https://github.com/craftcms/cms/security/advisories/GHSA-7x43-mpfg-r9wj
- https://nvd.nist.gov/vuln/detail/CVE-2026-28696
- https://github.com/craftcms/cms/commit/4d98a07e47580f1712095825d3e3c4d67bc9f8b9
- https://github.com/craftcms/cms
