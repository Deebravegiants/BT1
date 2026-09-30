# [?] vendor: update go-stack to fix a sigpanic panic (#14790)

## Summary
Severity: Unknown
Chain: Scroll
Component: scroll-tech/go-ethereum
Published: 2017-07-11
Source: https://github.com/scroll-tech/go-ethereum/commit/bd01cd7183e771984fb9c008e7a7ebf0a0c3f9ba
Type: security-commit

## Details
vendor: update go-stack to fix a sigpanic panic (#14790)

## Patch
### vendor/github.com/go-stack/stack/LICENSE.md
```diff
@@ -1,13 +1,21 @@
-Copyright 2014 Chris Hines
+The MIT License (MIT)
 
-Licensed under the Apache License, Version 2.0 (the "License");
-you may not use this file except in compliance with the License.
-You may obtain a copy of the License at
+Copyright (c) 2014 Chris Hines
 
-   http://www.apache.org/licenses/LICENSE-2.0
+Permission is hereby granted, free of charge, to any person obtaining a copy
+of this software and associated documentation files (the "Software"), to deal
+in the Software without restriction, including without limitation the rights
+to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
+copies of the Software, and to permit persons to whom the Software is
+furnished to do so, subject to the following conditions:
 
-Unless required by applicable law or agreed to in writing, software
-distributed under the License is distributed on an "AS IS" BASIS,
-WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
-See the License for the specific language governing permissions and
-limitations under the License.
+The above copyright notice and this permission notice shall be included in all
+copies or substantial portions of the Software.
+
+THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
+IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
+FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
+AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
+LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
+OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
+SOFTWARE.
```

### vendor/github.com/go-stack/stack/stack.go
```diff
@@ -39,7 +39,7 @@ func Caller(skip int) Call {
 	}
 
 	c.pc = pcs[1]
-	if runtime.FuncForPC(pcs[0]) != sigpanic {
+	if runtime.FuncForPC(pcs[0]).Name() != "runtime.sigpanic" {
 		c.pc--
 	}
 	c.fn = runtime.FuncForPC(c.pc)
@@ -205,33 +205,6 @@ func (cs CallStack) Format(s fmt.State, verb rune) {
 	s.Write(closeBracketBytes)
 }
 
-// findSigpanic intentionally executes faulting code to generate a stack trace
-// containing an entry for runtime.sigpanic.
-func findSigpanic() *runtime.Func {
-	var fn *runtime.Func
-	var p *int
-	func() int {
-		defer func() {
-			if p := recover(); p != nil {
-				var pcs [512]uintptr
-				n := runtime.Callers(2, pcs[:])
-				for _, pc := range pcs[:n] {
-					f := runtime.FuncForPC(pc)
-					if f.Name() == "runtime.sigpanic" {
-						fn = f
-						break
-					}
-				}
-			}
-		}()
-		// intentional nil pointer dereference to trigger sigpanic
-		return *p
-	}()
-	return fn
-}
-
-var sigpanic = findSigpanic()
-
 // Trace returns a CallStack for the current goroutine with element 0
 // identifying the calling function.
 func Trace() CallStack {
@@ -241,7 +214,7 @@ func Trace() CallStack {
 
 	for i, pc := range pcs[:n] {
 		pcFix := pc
-		if i > 0 && cs[i-1].fn != sigpanic {
+		if i > 0 && cs[i-1].fn.Name() != "runtime.sigpanic" {
 			pcFix--
 		}
 		cs[i] = Call{
```

### vendor/vendor.json
```diff
@@ -99,10 +99,10 @@
 			"revisionTime": "2017-01-17T22:23:42Z"
 		},
 		{
-			"checksumSHA1": "2sj/DbXoXdnPAfjAEyhS0Jj5QL0=",
+			"checksumSHA1": "KZ3QD2QgUS4RcoKiA3mn5pSlJxQ=",
 			"path": "github.com/go-stack/stack",
-			"revision": "100eb0c0a9c5b306ca2fb4f165df21d80ada4b82",
-			"revisionTime": "2016-05-14T03:44:11Z"
+			"revision": "54be5f394ed2c3e19dac9134a40a95ba5a017f7b",
+			"revisionTime": "2017-07-10T16:04:46Z"
 		},
 		{
 			"checksumSHA1": "p/8vSviYF91gFflhrt5vkyksroo=",
```
