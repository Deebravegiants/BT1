# [H] Directus incorrectly handles `_in` filter

## Summary
Severity: High
Advisory: GHSA-hxgm-ghmv-xjjm
CVE: CVE-2024-39701
CWE: CWE-284
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2024-07-08
Source: https://github.com/advisories/GHSA-hxgm-ghmv-xjjm
Type: github-advisory

## Affected
- npm: `directus` — affected >=9.23.0 <10.6.0

## Details
### Summary
Directus >=9.23.0, <=v10.5.3 improperly handles _in, _nin operators.
It evaluates empty arrays as valid so expressions like {"role": {"_in": $CURRENT_USER.some_field}} would evaluate to true allowing the request to pass.

### Details
This results in Broken Access Control because the rule fails to do what it was intended to do: Pass rule if **field** matches any of the **values**. ref: https://docs.directus.io/reference/filter-rules.html#filter-operators
In my example this would translate to "Pass rule if **<collection>.role** matches any of **[]**". Which should fail. This instead passes in Directus <= v10.5.3, >=v9.23.0

### PoC
{"role": {"_in": $CURRENT_USER.some_field}} field validation would pass if $CURRENT_USER.some_field is null.

Real scenario: Using https://github.com/u12206050/directus-extension-role-chooser with the specified versions of Directus (I tested on 10.0.0) allows users with access to this feature set their role to whatever role if they don't have any roles assigned (user_roles.role is left with the default value, null) despite the validation rule being 
```yaml
validation:
    role:
      _in: $CURRENT_USER.user_roles.role
```
Latest version of Directus (v10.8.3 and above) handles the above validation rule correctly.

### Impact
Permissions fail to open for setups relying on this filter and can lead to users getting access to things they're not supposed to.

## References
- https://github.com/directus/directus/security/advisories/GHSA-hxgm-ghmv-xjjm
- https://nvd.nist.gov/vuln/detail/CVE-2024-39701
- https://github.com/directus/directus
