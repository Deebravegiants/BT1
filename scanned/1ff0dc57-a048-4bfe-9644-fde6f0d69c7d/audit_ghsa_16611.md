# [M] Directus allows redacted data extraction on the API through "alias"

## Summary
Severity: Medium
Advisory: GHSA-p8v3-m643-4xqx
CVE: CVE-2024-34708
CWE: CWE-200
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-05-13
Source: https://github.com/advisories/GHSA-p8v3-m643-4xqx
Type: github-advisory

## Affected
- npm: `directus` — affected >=0 <10.11.0

## Details
## Summary
A user with permission to view any collection using redacted hashed fields can get access the raw stored version using the `alias` functionality on the API.
Normally, these redacted fields will return `**********` however  if we change the request to `?alias[workaround]=redacted` we can instead retrieve the plain text value for the field.

## Steps to reproduce
- Set up a simple role with read-access to users.
- Create a new user with the role from the previous step
- Assign a password to the user

The easiest way to confirm this vulnerability is by first visiting `/users/me`. You should be presented with a redacted JSON-object.
Next, visit `/users/me?alias[hash]=password`. This time, the returned JSON object will included the raw password hash instead of the redacted value.

## Workaround
This can be avoided by removing permission to view the sensitive fields entirely from users or roles that should not be able to see them.

## References
- https://github.com/directus/directus/security/advisories/GHSA-p8v3-m643-4xqx
- https://nvd.nist.gov/vuln/detail/CVE-2024-34708
- https://github.com/directus/directus/commit/e70a90c267bea695afce6545174c2b77517d617b
- https://github.com/directus/directus
