# [M] Windows only: arbitrary file read vulnerability in openssl s_server

## Summary
Severity: Medium (CVSS 5.9)
Program: Internet Bug Bounty
Weakness: Path Traversal
Reporter: jobert
State: resolved
Disclosed: 2020-10-10T03:39:09.695Z
Source: https://hackerone.com/reports/850775

## Details
==(Copied from an email sent to openssl-security@openssl.org on August 15, 2019)==

Hi,

There's an arbitrary file read vulnerability present in openssl s_server when ran on Windows with the -WWW or -HTTP option. To reproduce:

* run `openssl s_server -tls1 -WWW -accept 443`
* run `.\curl.exe -k https://127.0.0.1/..\..\..\..\..\..\..\any-file`
* observe the contents of any-file, which could be located outside of the running directory, to be returned to the user

The root cause of this vulnerability seems to come from an incomplete check in path parsing logic: https://github.com/openssl/openssl/blob/master/apps/s_server.c#L3225. Ideally, it'd include a check for a backslash, too. It seems that this particular code has been around for some time.

Vulnerable versions seem to include 0.9.6, 0.9.7, 0.9.8, 1.0.0, 1.0.1, 1.0.2, 1.1.0, and 1.1.1.

This was tested against OpenSSL 1.1.1c on Windows 10 (64-bit).

The maintainers fixed this in [this commit](https://github.com/openssl/openssl/commit/0a4d6c67480a4d2fce514e08d3efe571f2ee99c9):

```diff
diff --git a/apps/s_server.c b/apps/s_server.c
index 038046808037..5f58ef68fefa 100644
--- a/apps/s_server.c
+++ b/apps/s_server.c
@@ -3211,6 +3211,12 @@ static int www_body(int s, int stype, int prot, unsigned char *context)
                 if (e[0] == ' ')
                     break;
 
+                if (e[0] == ':') {
+                    /* Windows drive. We treat this the same way as ".." */
+                    dot = -1;
+                    break;
+                }
+
                 switch (dot) {
                 case 1:
                     dot = (e[0] == '.') ? 2 : 0;
@@ -3219,11 +3225,11 @@ static int www_body(int s, int stype, int prot, unsigned char *context)
                     dot = (e[0] == '.') ? 3 : 0;
```

_Trimmed to 38 lines — full report: https://hackerone.com/reports/850775_
