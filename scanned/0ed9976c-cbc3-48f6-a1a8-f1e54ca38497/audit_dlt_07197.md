# [?] Release notes for vulnerability and -maxtimeadjustment option.

## Summary
Severity: Unknown
Chain: Zcash
Component: zcash/zcash
Published: 2020-02-04
Source: https://github.com/zcash/zcash/commit/3d8af86c2c9589f9d118225d9e9a66a38120c0ca
Type: security-commit

## Details
Release notes for vulnerability and -maxtimeadjustment option.

Co-authored-by: Daira Hopwood <daira@jacaranda.org>
Co-authored-by: Sean Bowe <ewillbefull@gmail.com>
Signed-off-by: Daira Hopwood <daira@jacaranda.org>

## Patch
### doc/release-notes.md
```diff
@@ -4,3 +4,12 @@ release-notes at release time)
 Notable changes
 ===============
 
+This release fixes a security issue described at
+https://z.cash/support/security/announcements/security-announcement-2020-02-05/ .
+
+This release also adds a `-maxtimeadjustment` option to set the maximum time, in
+seconds, by which the node's clock can be adjusted based on the clocks of its
+peer nodes. This option defaults to 0, meaning that no such adjustment is performed.
+This is a change from the previous behaviour, which was to adjust the clock by up
+to 70 minutes forward or backward. The maximum setting for this option is now
+25 minutes (1500 seconds).
```
