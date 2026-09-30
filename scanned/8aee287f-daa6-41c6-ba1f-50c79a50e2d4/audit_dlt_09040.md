# [?] release(runway): cherry-pick bump: socks to 2.8.8 to resolve ip-address XSS vulnerability (#42477)

## Summary
Severity: Unknown
Chain: MetaMask
Component: MetaMask/metamask-extension
Published: 2026-05-06
Source: https://github.com/MetaMask/metamask-extension/commit/b3e24114a017cce01a33c0916f17fa6c97ab8852
Type: security-commit

## Details
release(runway): cherry-pick bump: socks to 2.8.8 to resolve ip-address XSS vulnerability (#42477)

- bump: socks to 2.8.8 to resolve ip-address XSS vulnerability (#42464)

## Patch
### attribution.txt
```diff
@@ -16109,7 +16109,7 @@ SOFTWARE.
 ******************************
 
 ip-address
-9.0.5 <https://github.com/beaugunderson/ip-address>
+10.2.0 <https://github.com/beaugunderson/ip-address>
 Copyright (C) 2011 by Beau Gunderson
 
 Permission is hereby granted, free of charge, to any person obtaining a copy
@@ -17716,52 +17716,6 @@ jsbi
    END OF TERMS AND CONDITIONS
 
 
-******************************
-
-jsbn
-1.1.0 <https://github.com/andyperlitch/jsbn>
-Licensing
----------
-
-This software is covered under the following copyright:
-
-/*
- * Copyright (c) 2003-2005  Tom Wu
- * All Rights Reserved.
- *
- * Permission is hereby granted, free of charge, to any person obtaining
- * a copy of this software and associated documentation files (the
- * "Software"), to deal in the Software without restriction, including
- * without limitation the rights to use, copy, modify, merge, publish,
- * distribute, sublicense, and/or sell copies of the Software, and to
- * permit persons to whom the Software is furnished to do so, subject to
- * the following conditions:
- *
- * The above copyright notice and this permission notice shall be
- * included in all copies or substantial portions of the Software.
- *
- * THE SOFTWARE IS PROVIDED "AS-IS" AND WITHOUT WARRANTY OF ANY KIND, 
- * EXPRESS, IMPLIED OR OTHERWISE, INCLUDING WITHOUT LIMITATION, ANY 
- * WARRANTY OF MERCHANTABILITY OR FITNESS FOR A PARTICULAR PURPOSE.  
- *
- * IN NO EVENT SHALL TOM WU BE LIABLE FOR ANY SPECIAL, INCIDENTAL,
- * INDIRECT OR CONSEQUENTIAL DAMAGES OF ANY KIND, OR ANY DAMAGES WHATSOEVER
- * RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER OR NOT ADVISED OF
- * THE POSSIBILITY OF DAMAGE, AND ON ANY THEORY OF LIABILITY, ARISING OUT
- * OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
- *
- * In addition, the following condition applies:
- *
- * All redistributions must retain an intact copy of this copyright notice
- * and disclaimer.
- */
-
-Address all questions regarding this license to:
-
-  Tom Wu
-  tjw@cs.Stanford.EDU
-
-
 ******************************
 
 jsesc
@@ -34611,7 +34565,7 @@ CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
 ******************************
 
 socks
-2.8.4 <https://github.com/JoshGlazebrook/socks>
+2.8.8 <https://github.com/JoshGlazebrook/socks>
 The MIT License (MIT)
 
 Copyright (c) 2013 Josh Glazebrook
@@ -36362,36 +36316,6 @@ TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
 SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
 
 
-******************************
-
-sprintf-js
-1.1.3 <https://github.com/alexei/sprintf.js>
-Copyright (c) 2007-present, Alexandru Mărășteanu <hello@alexei.ro>
-All rights reserved.
-
-Redistribution and use in source and binary forms, with or without
-modification, are permitted provided that the following conditions are met:
-* Redistributions of source code must retain the above copyright
-  notice, this list of conditions and the following disclaimer.
-* Redistributions in binary form must reproduce the above copyright
-  notice, this list of conditions and the following disclaimer in the
-  documentation and/or other materials provided with the distribution.
-* Neither the name of this software nor the names of its contributors may be
-  used to endorse or promote products derived from this software without
-  specific prior written permission.
-
-THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
-ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
-WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
-DISCLAIMED. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR
-ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
-(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
-LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
-ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
-(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
-SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
-
-
 ******************************
 
 @spruceid/siwe-parser
```

### yarn.lock
```diff
@@ -30039,13 +30039,10 @@ __metadata:
   languageName: node
   linkType: hard
 
-"ip-address@npm:^9.0.5":
-  version: 9.0.5
-  resolution: "ip-address@npm:9.0.5"
-  dependencies:
-    jsbn: "npm:1.1.0"
-    sprintf-js: "npm:^1.1.3"
-  checksum: 10/1ed81e06721af012306329b31f532b5e24e00cb537be18ddc905a84f19fe8f83a09a1699862bf3a1ec4b9dea93c55a3fa5faf8b5ea380431469df540f38b092c
+"ip-address@npm:^10.1.1":
+  version: 10.2.0
+  resolution: "ip-address@npm:10.2.0"
+  checksum: 10/12fec399e1af5753ac322e47a6d81a50d3a528b3abb17c09525b2a2edcaedcca628c40520706f7037bc4d8e951b0296c47e7b86d0a8e6e2335c8f0ba4afcfac1
   languageName: node
   linkType: hard
 
@@ -32071,13 +32068,6 @@ __metadata:
   languageName: node
   linkType: hard
 
-"jsbn@npm:1.1.0":
-  version: 1.1.0
-  resolution: "jsbn@npm:1.1.0"
-  checksum: 10/bebe7ae829bbd586ce8cbe83501dd8cb8c282c8902a8aeeed0a073a89dc37e8103b1244f3c6acd60278bcbfe12d93a3f83c9ac396868a3b3bbc3c5e5e3b648ef
-  languageName: node
-  linkType: hard
-
 "jscodeshift@npm:^0.15.1":
   version: 0.15.2
   resolution: "jscodeshift@npm:0.15.2"
@@ -41910,12 +41900,12 @@ __metadata:
   linkType: hard
 
 "socks@npm:^2.6.2, socks@npm:^2.8.3":
-  version: 2.8.4
-  resolution: "socks@npm:2.8.4"
+  version: 2.8.8
+  resolution: "socks@npm:2.8.8"
   dependencies:
-    ip-address: "npm:^9.0.5"
+    ip-address: "npm:^10.1.1"
     smart-buffer: "npm:^4.2.0"
-  checksum: 10/ab3af97aeb162f32c80e176c717ccf16a11a6ebb4656a62b94c0f96495ea2a1f4a8206c04b54438558485d83d0c5f61920c07a1a5d3963892a589b40cc6107dd
+  checksum: 10/2108b9bd9cd3ab3248704a8319c875681bd8219afb13ae29648810193e4f3a24432baf20364eda1cb8ec144f2e1f3eb0692ce53281f05fe29aff5385e60b9b42
   languageName: node
   linkType: hard
 
```
