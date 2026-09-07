# [M] Vantage6: Set admin user and password from environment or configuration

## Summary
Severity: Medium
Advisory: GHSA-fgmc-2hqj-86v4
CVE: CVE-2026-54445
CWE: CWE-1393, CWE-204
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:L/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-05
Source: https://github.com/advisories/GHSA-fgmc-2hqj-86v4
Type: github-advisory

## Affected
- PyPI: `vantage6` — affected >=0 <5.0.0

## Details
### Impact
Vantage6 currently provides an initial user with username `root` and password `root`. This is not ideal for the following reasons:
- Attackers know that almost all vantage6 servers have a user with username `root` that probably has admin rights
- The initial password is very weak and it is possible that administrators forget to reset it.

### Patches
No

### Workarounds
It is possible to delete the `root` user after it has been used to create other users

### References
We could consider doing this like [mongodb](https://hub.docker.com/_/mongo)

### Additional info

Luis uses the following patch to mitigate it:
```diff
diff --git a/vantage6-server/vantage6/server/__init__.py b/vantage6-server/vantage6/server/__init__.py
index ea362c1e..c6dcbbd9 100644
--- a/vantage6-server/vantage6/server/__init__.py
+++ b/vantage6-server/vantage6/server/__init__.py
@@ -618,18 +618,30 @@ class ServerApp:
             # TODO use constant instead of 'Root' literal
             root = db.Role.get_by_name("Root")
 
-            log.warn(
-                f"Creating root user: "
-                f"username={SUPER_USER_INFO['username']}, "
-                f"password={SUPER_USER_INFO['password']}"
-            )
+            # Temporary patch
+            # read initial root password from file (docker secret) if provided
+            # TODO: This is a workaround so we don't have an insecure vserver
+            #       at the start. Ideally, we would provide an already hashed
+            #       password. But as hashing is implemented via @validates on
+            #       the field 'password', there isn't a nice way around this.
+            if os.environ.get("V6_INITIAL_ROOT_PASSWORD_FILE"):
+                with open(
+                    os.environ.get("V6_INITIAL_ROOT_PASSWORD_FILE")
+                ) as password_file:
+                    initial_root_password = password_file.read().strip()
+                log.info(
+                    f"Creating root user with password provided via V6_INITIAL_ROOT_PASSWORD_FILE"
+                )
+            else:
+                initial_root_password = SUPER_USER_INFO["password"]
+                log.warn(f"Creating root user with default credentials!")
 
             user = db.User(
                 username=SUPER_USER_INFO["username"],
                 roles=[root],
                 organization=org,
                 email="root@domain.ext",
-                password=SUPER_USER_INFO["password"],
+                password=initial_root_password,
                 failed_login_attempts=0,
                 last_login_attempt=None,
             )
```

## References
- https://github.com/vantage6/vantage6/security/advisories/GHSA-fgmc-2hqj-86v4
- https://nvd.nist.gov/vuln/detail/CVE-2026-54445
- https://github.com/vantage6/vantage6/issues/1932
- https://github.com/vantage6/vantage6
- https://github.com/vantage6/vantage6/blob/main/docs/release_notes.rst#500
