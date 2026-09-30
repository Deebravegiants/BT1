# [M] ginuerzh/gost vulnerable to Timing Attack

## Summary
Severity: Medium
Advisory: GHSA-qjrq-hm79-49ww
CVE: CVE-2023-32691
CWE: CWE-203
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2023-05-22
Source: https://github.com/advisories/GHSA-qjrq-hm79-49ww
Type: github-advisory

## Affected
- Go: `github.com/ginuerzh/gost` — affected >=0

## Details
[Timing attacks](https://en.wikipedia.org/wiki/Timing_attack) occur when an attacker can guess a secret by observing a difference in processing time for valid and invalid inputs. Sensitive secrets such as passwords, token and API keys should be compared only using a constant-time comparision function.
More information on this attack type can be found in [this blog post](https://verboselogging.com/2012/08/20/a-timing-attack-in-action). 

# Root Cause Analysis

In this case, the vulnerability occurs due to the following code.

https://github.com/ginuerzh/gost/blob/1c62376e0880e4094bd3731e06bd4f7842638f6a/auth.go#L46-L46

Here, a untrusted input, sourced from a HTTP header, is compared directly with a secret. 
Since, this comparision is not secure, an attacker can mount a side-channel timing attack to guess the password.

# Remediation

This can be easily fixed using a constant time comparing function such as `crypto/subtle`'s `ConstantTimeCompare`. 
An example fix can be found in https://github.com/runatlantis/atlantis/commit/48870911974adddaa4c99c8089e79b7d787fa820 Alternatively, one can apply the patch below

```
From d18cff85e1a565f688f717fd8f2cacea62ff9dbf Mon Sep 17 00:00:00 2001
From: Porcupiney Hairs <porcupiney.hairs@protonmail.com>
Date: Sun, 7 May 2023 01:03:33 +0530
Subject: [PATCH] Fix : Timing attack

---
 auth.go | 4 +++-
 1 file changed, 3 insertions(+), 1 deletion(-)

diff --git a/auth.go b/auth.go
index 1be96e9..be13f23 100644
--- a/auth.go
+++ b/auth.go
@@ -2,6 +2,7 @@ package gost
 
 import (
 	"bufio"
+	"crypto/subtle"
 	"io"
 	"strings"
 	"sync"
@@ -43,7 +44,8 @@ func (au *LocalAuthenticator) Authenticate(user, password string) bool {
 	}
 
 	v, ok := au.kvs[user]
-	return ok && (v == "" || password == v)
+	passOk := subtle.ConstantTimeCompare([]byte(password), []byte(v)) == 0
+	return ok && (v == "" || passOk)
 }
 
 // Add adds a key-value pair to the Authenticator.
-- 
2.25.1

```

## References
- https://github.com/ginuerzh/gost/security/advisories/GHSA-qjrq-hm79-49ww
- https://nvd.nist.gov/vuln/detail/CVE-2023-32691
- https://github.com/ginuerzh/gost
- https://github.com/ginuerzh/gost/blob/1c62376e0880e4094bd3731e06bd4f7842638f6a/auth.go#L46
