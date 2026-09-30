# [?] doc: Fill in details about miniupnp CVE-2017-8798

## Summary
Severity: Unknown
Chain: Dogecoin
Component: dogecoin/dogecoin
Published: 2017-06-07
Source: https://github.com/dogecoin/dogecoin/commit/7a643511b474d53f952d3cd403af51aabd104044
Type: security-commit

## Details
doc: Fill in details about miniupnp CVE-2017-8798

## Patch
### doc/release-notes.md
```diff
@@ -33,7 +33,17 @@ Notable changes
 miniupnp CVE-2017-8798
 ----------------------------
 
-[todo]
+Bundled miniupnpc was updated to 2.0.20170509. This fixes an integer signedness error
+(present in MiniUPnPc v1.4.20101221 through v2.0) that allows remote attackers
+(within the LAN) to cause a denial of service or possibly have unspecified
+other impact.
+
+This only affects users that have explicitly enabled UPnP through the GUI
+setting or through the `-upnp` option, as since the last UPnP vulnerability
+(in Bitcoin Core 0.10.3) it has been disabled by default.
+
+If you use this option, it is recommended to upgrade to this version as soon as
+possible.
 
 0.14.2 Change log
 =================
@@ -48,10 +58,10 @@ git merge commit are mentioned.
 
 ### P2P protocol and network code
 - #10424 `37a8fc5` Populate services in GetLocalAddress (morcos)
-- #10441 `9e3ad50` net: only enforce expected services for half of outgoing connections (theuni)
+- #10441 `9e3ad50` Only enforce expected services for half of outgoing connections (theuni)
 
 ### Build system
-- #10414 `ffb0c4b` [depends] miniupnpc 2.0.20170509 (fanquake)
+- #10414 `ffb0c4b` miniupnpc 2.0.20170509 (fanquake)
 - #10228 `ae479bc` Regenerate bitcoin-config.h as necessary (theuni)
 
 ### Miscellaneous
```
