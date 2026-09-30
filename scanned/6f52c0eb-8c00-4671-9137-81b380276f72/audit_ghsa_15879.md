# [M] @saltcorn/server arbitrary file and directory listing when accessing build mobile app results

## Summary
Severity: Medium
Advisory: GHSA-cfqx-f43m-vfh7
CWE: CWE-548
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-10-03
Source: https://github.com/advisories/GHSA-cfqx-f43m-vfh7
Type: github-advisory

## Affected
- npm: `@saltcorn/server` — affected >=0 <1.0.0-beta.14

## Details
### Summary

A user with admin permission can read arbitrary file and directory names on the filesystem by calling the `admin/build-mobile-app/result?build_dir_name=` endpoint.  The `build_dir_name` parameter is not properly validated and it's then used to construct the `buildDir` that is read. The file/directory names under the `buildDir` will be returned. 

### Details

- file: https://github.com/saltcorn/saltcorn/blob/v1.0.0-beta.13/packages/server/routes/admin.js#L2884-L2893

```js
router.get(
  "/build-mobile-app/result",
  isAdmin,
  error_catcher(async (req, res) => {
    const { build_dir_name } = req.query; // [1] source
    const rootFolder = await File.rootFolder();
    const buildDir = path.join(
      rootFolder.location,
      "mobile_app",
      build_dir_name // [2]
    );
    const files = await Promise.all(
      fs
        .readdirSync(buildDir) // [3] sink
        .map(async (outFile) => await File.from_file_on_disk(outFile, buildDir))
    );
    [...]
  })
);
```

### PoC

- log into the application as an admin user
- visit the following url: `http://localhost:3000/admin/build-mobile-app/result?build_dir_name=/../../../../../../../../`


**NOTE**: it's possible to only see file and directory names but not to download their content.

### Impact

Information disclosure

### Recommended Mitigation

Resolve the `buildDir` and check if it starts with `${rootFolder.location}/mobile_app`.

## References
- https://github.com/saltcorn/saltcorn/security/advisories/GHSA-cfqx-f43m-vfh7
- https://github.com/saltcorn/saltcorn/commit/81adaf78430a9b59804894574d67d2a0c7bb3dc5
- https://github.com/saltcorn/saltcorn
- https://github.com/saltcorn/saltcorn/blob/v1.0.0-beta.13/packages/server/routes/admin.js#L2884-L2893
