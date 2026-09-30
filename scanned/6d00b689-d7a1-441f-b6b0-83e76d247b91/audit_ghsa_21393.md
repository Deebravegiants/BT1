# [C] Field-level access-control bypass for multiselect field

## Summary
Severity: Critical
Advisory: GHSA-6mhr-52mv-6v6f
CVE: CVE-2022-39322
CWE: CWE-285, CWE-863
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2022-10-18
Source: https://github.com/advisories/GHSA-6mhr-52mv-6v6f
Type: github-advisory

## Affected
- npm: `@keystone-6/core` — affected >=2.2.0 <2.3.1

## Details
#### Impact

`@keystone-6/core@2.2.0 || 2.3.0` users who are using the `multiselect` field, and provided field-level access control - are vulnerable to their field-level access control not being used.

List-level access control is **NOT** affected.

Field-level access control for fields other than `multiselect` are **NOT** affected.

Example, **you are vulnerable if** you are using field-level access control on a `multiselect` like the following:
```ts
const yourList = list({
  access: {
    // this is list-level access control, this is NOT impacted
  },
  fields: {
    yourFieldName: multiselect({
      // this is field-level access control, for multiselect fields
      //   this is vulnerable
      access: {
        create: ({ session }) => session?.data.isAdmin,
        update: ({ session }) => session?.data.isAdmin,
      },
      options: [
        { value: 'apples', label: 'Apples' },
        { value: 'oranges', label: 'Oranges' },
      ],
      // ...
    }),
    // ...
  },
  // ...
});
```

#### Mitigation
Please upgrade to `@keystone-6/core >= 2.3.1`, where this vulnerability has been closed.

#### Workarounds
If for some reason you cannot upgrade your dependencies, you should stop using the `multiselect` field.

#### Credits
Thanks to [Marek R](https://github.com/marekryb) for reporting and submitting the pull request to fix this problem.

If you have any questions around this security advisory, please don't hesitate to contact us at [security@keystonejs.com](mailto:security@keystonejs.com), or [open an issue on GitHub](https://github.com/keystonejs/keystone/issues/new/choose).

If you have a security flaw to report for any software in this repository, please see our [SECURITY policy](https://github.com/keystonejs/keystone/blob/main/SECURITY.md).

## References
- https://github.com/keystonejs/keystone/security/advisories/GHSA-6mhr-52mv-6v6f
- https://nvd.nist.gov/vuln/detail/CVE-2022-39322
- https://github.com/keystonejs/keystone/commit/65c6ee3deef23605fc72b80230908696a7a65e7c
- https://github.com/keystonejs/keystone
