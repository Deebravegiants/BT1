# [M] OpenSSL::X509::Name Equality Check Does Not Work, Patch included

## Summary
Severity: Medium
Program: Ruby
Weakness: Improper Certificate Validation
Reporter: tylereckstein
State: resolved
Disclosed: 2018-10-19T21:59:23.989Z
CVE: CVE-2018-16395
Source: https://hackerone.com/reports/387250

## Details
When two OpenSSL::X509::Name objects are compared using ==, depending on the ordering, non-equal objects will return true. When the first argument is one character longer than the second, or the second argument contains a character that is one less than a character in the same position of the first argument, the result of == will be true. Example below:

irb(main):001:0> require 'openssl'
=> true
irb(main):002:0> a = OpenSSL::X509::Name.new([["CN", "www.example.com"]])
=> #<OpenSSL::X509::Name:0x007fa127cdf3f0>
irb(main):003:0> b = OpenSSL::X509::Name.new([["CN", "www.example.co"]])
=> #<OpenSSL::X509::Name:0x007fa127cd0260>
irb(main):004:0> c = OpenSSL::X509::Name.new([["CN", "www.exbmple.com"]])
=> #<OpenSSL::X509::Name:0x007fa127cb68b0>
irb(main):005:0> a == b
=> true                    # Should NOT be true
irb(main):006:0> a == c
=> false
irb(main):007:0> c == a
=> true                    # Should NOT be true
irb(main):008:0> b == a
=> false



This appears to be from the ossl_x509name_cmp function and I was able to fix this with the following diff, with included tests that would fail without the change to ossl_x509name_cmp:

diff --git a/ext/openssl/ossl_x509name.c b/ext/openssl/ossl_x509name.c
index c900bcb..15e4bb0 100644
--- a/ext/openssl/ossl_x509name.c
+++ b/ext/openssl/ossl_x509name.c
@@ -400,7 +400,7 @@ ossl_x509name_cmp(VALUE self, VALUE other)

     result = ossl_x509name_cmp0(self, other);
     if (result < 0) return INT2FIX(-1);
-    if (result > 1) return INT2FIX(1);
+    if (result > 0) return INT2FIX(1);

     return INT2FIX(0);
 }
diff --git a/test/test_x509name.rb b/test/test_x509name.rb
index 2d92e64..ae8a8fb 100644

_Trimmed to 38 lines — full report: https://hackerone.com/reports/387250_
