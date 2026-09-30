# [?] Fix large integer overflows in swagger-ui

## Summary
Severity: Unknown
Chain: Ergo
Component: ergoplatform/ergo
Published: 2023-12-18
Source: https://github.com/ergoplatform/ergo/commit/13cb4bbfd06ba3699be3a5f5d044c10750fba52f
Type: security-commit

## Details
Fix large integer overflows in swagger-ui

The swagger-ui distfiles are taken from https://github.com/SethDusek/swagger-ui

## Patch
### src/main/resources/swagger-ui/oauth2-redirect.html
```diff
@@ -1,8 +1,9 @@
 <!doctype html>
 <html lang="en-US">
-<body onload="run()">
-</body>
-</html>
+<head>
+    <title>Swagger UI: OAuth2 Redirect</title>
+</head>
+<body>
 <script>
     'use strict';
     function run () {
@@ -12,31 +13,32 @@
         var isValid, qp, arr;
 
         if (/code|token|error/.test(window.location.hash)) {
-            qp = window.location.hash.substring(1);
+            qp = window.location.hash.substring(1).replace('?', '&');
         } else {
             qp = location.search.substring(1);
         }
 
-        arr = qp.split("&")
-        arr.forEach(function (v,i,_arr) { _arr[i] = '"' + v.replace('=', '":"') + '"';})
+        arr = qp.split("&");
+        arr.forEach(function (v,i,_arr) { _arr[i] = '"' + v.replace('=', '":"') + '"';});
         qp = qp ? JSON.parse('{' + arr.join() + '}',
                 function (key, value) {
-                    return key === "" ? value : decodeURIComponent(value)
+                    return key === "" ? value : decodeURIComponent(value);
                 }
-        ) : {}
+        ) : {};
 
-        isValid = qp.state === sentState
+        isValid = qp.state === sentState;
 
         if ((
-          oauth2.auth.schema.get("flow") === "accessCode"||
-          oauth2.auth.schema.get("flow") === "authorizationCode"
+          oauth2.auth.schema.get("flow") === "accessCode" ||
+          oauth2.auth.schema.get("flow") === "authorizationCode" ||
+          oauth2.auth.schema.get("flow") === "authorization_code"
         ) && !oauth2.auth.code) {
             if (!isValid) {
                 oauth2.errCb({
                     authId: oauth2.auth.name,
                     source: "auth",
                     level: "warning",
-                    message: "Authorization may be unsafe, passed state was changed in server Passed state wasn't returned from auth server"
+                    message: "Authorization may be unsafe, passed state was changed in server. The passed state wasn't returned from auth server."
                 });
             }
 
@@ -45,7 +47,7 @@
                 oauth2.auth.code = qp.code;
                 oauth2.callback({auth: oauth2.auth, redirectUrl: redirectUrl});
             } else {
-                let oauthErrorMsg
+                let oauthErrorMsg;
                 if (qp.error) {
                     oauthErrorMsg = "["+qp.error+"]: " +
                         (qp.error_description ? qp.error_description+ ". " : "no accessCode received from the server. ") +
@@ -56,12 +58,22 @@
                     authId: oauth2.auth.name,
                     source: "auth",
                     level: "error",
-                    message: oauthErrorMsg || "[Authorization failed]: no accessCode received from the server"
+                    message: oauthErrorMsg || "[Authorization failed]: no accessCode received from the server."
                 });
             }
         } else {
             oauth2.callback({auth: oauth2.auth, token: qp, isValid: isValid, redirectUrl: redirectUrl});
         }
         window.close();
     }
+
+    if (document.readyState !== 'loading') {
+        run();
+    } else {
+        document.addEventListener('DOMContentLoaded', function () {
+            run();
+        });
+    }
 </script>
+</body>
+</html>
```
