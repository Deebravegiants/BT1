# [H] Unauthorized Access to Private Fields in User Registration API

## Summary
Severity: High
Advisory: GHSA-gc7p-j5xm-xxh2
CVE: CVE-2023-39345
CWE: CWE-287
Ecosystem: npm
CVSS: CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:L/I:H/A:L (CVSS_V3)
Published: 2023-11-03
Source: https://github.com/advisories/GHSA-gc7p-j5xm-xxh2
Type: github-advisory

## Affected
- npm: `@strapi/plugin-users-permissions` — affected >=4.0.0 <4.13.1
- npm: `@strapi/strapi` — affected >=4.0.0 <4.13.1

## Details
### System Details
| Name     | Value                  |
|----------|------------------------|
| OS       | Windows 11             |
| Version  | 4.11.1 (node v16.14.2) |
| Database | mysql                  |


### Description
I marked some fields as private fields in user content-type, and tried to register as a new user via api, at the same time I added content to fill the private fields and sent a post request, and as you can see from the images below, I can write to the private fields.

![register](https://user-images.githubusercontent.com/32245914/246987508-9337ffd5-c681-4f51-9a0b-2490b424ca1e.png)

![user](https://user-images.githubusercontent.com/32245914/246987564-9f440b3f-a7a3-4710-9b75-0854667fc35d.png)

![private_field](https://user-images.githubusercontent.com/32245914/246987590-9c0ecefd-fd64-4221-b642-e730ea55d440.png)

![table](https://user-images.githubusercontent.com/32245914/246987604-009e6808-5690-458e-aa87-57dda7d4589d.png)

To prevent this, I went to the extension area and tried to extend the register method, for this I wanted to do it using the sanitizeInput function that I know in the source codes of the strap. But the sanitizeInput function did not filter out private fields.

```js
  const { auth } = ctx.state;
  const data = ctx.request.body;
  const userSchema = strapi.getModel("plugin::users-permissions.user");

  sanitize.contentAPI.input(data, userSchema, { auth });
```

here's the solution I've temporarily kept to myself, code snippet

```js
  const body = ctx.request.body;

  const { attributes } = strapi.getModel("plugin::users-permissions.user");

  const sanitizedData = _.omitBy(body, (data, key) => {
    const attribute = attributes[key];

    if (_.isNil(attribute)) {
      return false;
    }

    //? If you want, you can throw an error for fields that we did not expect.

    // if (_.isNil(attribute))
    //   throw new ApplicationError(`Unexpected value ${key}`);

    // if private value is true, we do not want to send it to the database.
    return attribute.private;
  });

  return sanitizedData;
```

## References
- https://github.com/strapi/strapi/security/advisories/GHSA-gc7p-j5xm-xxh2
- https://nvd.nist.gov/vuln/detail/CVE-2023-39345
- https://github.com/strapi/strapi
- https://strapi.io/blog/security-disclosure-of-vulnerabilities-sept-2023
