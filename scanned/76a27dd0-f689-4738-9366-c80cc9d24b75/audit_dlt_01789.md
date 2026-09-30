# [?] Adjust OpenSSL defaults and mitigate CVE-2021-3499:

## Summary
Severity: Unknown
Chain: XRP
Component: XRPLF/rippled
Published: 2021-03-30
Source: https://github.com/XRPLF/rippled/commit/79e69da3647019840dca49622621c3d88bc3883f
Type: security-commit

## Details
Adjust OpenSSL defaults and mitigate CVE-2021-3499:

In order to effectively mitigate CVE-2021-3499 even when compiling
against versions of OpenSSL prior to 1.1.1k, this commit:

1) requires use of TLS 1.2 or later. Note that both TLS 1.0 and
   TLS 1.1 have been officially deprecated for over a year.
2) disables renegotiation support for TLS 1.2 connections.

Lastly, this commit also changes the default list of ciphers that
the server offers, limiting it only to ciphers that are part of
TLS 1.2.

## Patch
### src/ripple/basics/impl/make_SSLContext.cpp
```diff
@@ -29,13 +29,21 @@ namespace ripple {
 namespace openssl {
 namespace detail {
 
-// We limit the ciphers we request and allow to ensure that weak
-// ciphers aren't used. While this isn't strictly necessary for
-// the rippled server-server use case, where we only need MITM
-// detection/prevention, we also have websocket and rpc scenarios
-// and want to ensure weak ciphers can't be used.
-std::string const defaultCipherList =
-    "HIGH:MEDIUM:!aNULL:!MD5:!DSS:!3DES:!RC4:!EXPORT";
+/** The default list of ciphers we accept over TLS.
+
+    Generally we include cipher suites that are part of TLS v1.2, but
+    we specifically exclude:
+
+    - the DSS cipher suites (!DSS);
+    - cipher suites using pre-shared keys (!PSK);
+    - cipher suites that don't offer encryption (!eNULL); and
+    - cipher suites that don't offer authentication (!aNULL).
+
+    @note Server administrators can override this default list, on either a
+          global or per-port basis, using the `ssl_ciphers` directive in the
+          config file.
+ */
+std::string const defaultCipherList = "TLSv1.2:!DSS:!PSK:!eNULL:!aNULL";
 
 template <class>
 struct custom_delete;
@@ -194,69 +202,6 @@ ssl_ctx_use_privatekey(SSL_CTX* const ctx, evp_pkey_ptr key)
         LogicError("SSL_CTX_use_PrivateKey failed");
 }
 
-#ifdef SSL_FLAGS_NO_RENEGOTIATE_CIPHERS
-static bool
-disallowRenegotiation(SSL const* ssl, bool isNew)
-{
-    // Track when SSL connections have last negotiated and
-    // do not allow a connection to renegotiate more than
-    // once every 4 minutes
-    struct StaticData
-    {
-        std::mutex lock;
-        beast::aged_unordered_set<SSL const*> set;
-
-        StaticData() : set(ripple::stopwatch())
-        {
-        }
-    };
-
-    static StaticData sd;
-    std::lock_guard lock(sd.lock);
-    auto const expired(sd.set.clock().now() - std::chrono::minutes(4));
-
-    // Remove expired entries
-    for (auto iter(sd.set.chronological.begin());
-         (iter != sd.set.chronological.end()) && (iter.when() <= expired);
-         iter = sd.set.chronological.begin())
-    {
-        sd.set.erase(iter);
-    }
-
-    auto iter = sd.set.find(ssl);
-    if (iter != sd.set.end())
-    {
-        if (!isNew)
-        {
-            // This is a renegotiation and the last negotiation was recent
-            return true;
-        }
-
-        sd.set.touch(iter);
-    }
-    else
-    {
-        sd.set.emplace(ssl);
-    }
-
-    return false;
-}
-
-static void
-info_handler(SSL const* ssl, int event, int)
-{
-#if OPENSSL_VERSION_NUMBER < 0x10100000L
-    if ((ssl->s3) && (event & SSL_CB_HANDSHAKE_START))
-    {
-        if (disallowRenegotiation(ssl, SSL_in_before(ssl)))
-            ssl->s3->flags |= SSL3_FLAGS_NO_RENEGOTIATE_CIPHERS;
-    }
-#else
-    // empty, flag removed in OpenSSL 1.1
-#endif
-}
-#endif
-
 static std::string
 error_message(std::string const& what, boost::system::error_code const& ec)
 {
@@ -388,7 +333,10 @@ get_context(std::string const& cipherList)
         boost::asio::ssl::context::default_workarounds |
         boost::asio::ssl::context::no_sslv2 |
         boost::asio::ssl::context::no_sslv3 |
-        boost::asio::ssl::context::single_dh_use);
+        boost::asio::ssl::context::no_tlsv1 |
+        boost::asio::ssl::context::no_tlsv1_1 |
+        boost::asio::ssl::context::single_dh_use |
+        boost::asio::ssl::context::no_compression);
 
     {
         auto const& l = !cipherList.empty() ? cipherList : defaultCipherList;
@@ -435,9 +383,11 @@ get_context(std::string const& cipherList)
 
     SSL_CTX_set_tmp_dh(c->native_handle(), dh.get());
 
-#ifdef SSL_FLAGS_NO_RENEGOTIATE_CIPHERS
-    SSL_CTX_set_info_callback(c->native_handle(), info_handler);
-#endif
+    // Disable all renegotiation support in TLS v1.2. This can help prevent
+    // exploitation of the bug described in CVE-2021-3499 (for details see
+    // https://www.openssl.org/news/secadv/20210325.txt) when linking against
+    // OpenSSL versions prior to 1.1.1k.
+    SSL_CTX_set_options(c->native_handle(), SSL_OP_NO_RENEGOTIATION);
 
     return c;
 }
```
