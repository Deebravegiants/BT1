# [?] fixed race condition in test/helpers/test.method.js

## Summary
Severity: Unknown
Chain: Tooling
Component: web3/web3.js
Published: 2015-10-12
Source: https://github.com/web3/web3.js/commit/08e92c2aaafff91e1277021d6de7e31297d4ba7f
Type: security-commit

## Details
fixed race condition in test/helpers/test.method.js

## Patch
### test/helpers/test.method.js
```diff
@@ -1,7 +1,7 @@
 var chai = require('chai');
 var assert = chai.assert;
 var Web3 = require('../../index');
-var web3 = new Web3();
+
 var FakeHttpProvider = require('./FakeHttpProvider');
 var clone = function (object) { return JSON.parse(JSON.stringify(object)); };
 
@@ -15,9 +15,8 @@ var runTests = function (obj, method, tests) {
                 it('sync test: ' + index, function () {
                     
                     // given
-                    web3.reset();
                     var provider = new FakeHttpProvider();
-                    web3.setProvider(provider);
+                    var web3 = new Web3(provider);
                     provider.injectResult(test.result);
                     provider.injectValidation(function (payload) {
                         assert.equal(payload.jsonrpc, '2.0');
@@ -45,9 +44,8 @@ var runTests = function (obj, method, tests) {
                 it('async test: ' + index, function (done) {
                     
                     // given
-                    web3.reset();
                     var provider = new FakeHttpProvider();
-                    web3.setProvider(provider);
+                    var web3 = new Web3(provider);
                     provider.injectResult(test.result);
                     provider.injectValidation(function (payload) {
                         assert.equal(payload.jsonrpc, '2.0');
```
