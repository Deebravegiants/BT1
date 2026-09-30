# [?] fix(gateway_balances): handle overflow exception: (#4355)

## Summary
Severity: Unknown
Chain: XRP
Component: XRPLF/rippled
Published: 2023-03-16
Source: https://github.com/XRPLF/rippled/commit/10555faa928bc02400c22f1856ad1846b5d52f1a
Type: security-commit

## Details
fix(gateway_balances): handle overflow exception: (#4355)

* Prevent internal error by catching overflow exception in `gateway_balances`.
* Treat `gateway_balances` obligations overflow as max (largest valid) `STAmount`.
  * Note that very large sums of STAmount are approximations regardless.

---------

Co-authored-by: Scott Schurr <scott@ripple.com>

## Patch
### src/ripple/rpc/handlers/GatewayBalances.cpp
```diff
@@ -184,7 +184,23 @@ doGatewayBalances(RPC::JsonContext& context)
                         bal = -rs->getBalance();
                     }
                     else
-                        bal -= rs->getBalance();
+                    {
+                        try
+                        {
+                            bal -= rs->getBalance();
+                        }
+                        catch (std::runtime_error const&)
+                        {
+                            // Presumably the exception was caused by overflow.
+                            // On overflow return the largest valid STAmount.
+                            // Very large sums of STAmount are approximations
+                            // anyway.
+                            bal = STAmount(
+                                bal.issue(),
+                                STAmount::cMaxValue,
+                                STAmount::cMaxOffset);
+                        }
+                    }
                 }
             });
     }
```

### src/test/rpc/GatewayBalances_test.cpp
```diff
@@ -148,13 +148,69 @@ class GatewayBalances_test : public beast::unit_test::suite
         }
     }
 
+    void
+    testGWBOverflow()
+    {
+        using namespace std::chrono_literals;
+        using namespace jtx;
+        Env env(*this);
+
+        // Gateway account and assets
+        Account const alice{"alice"};
+        env.fund(XRP(10000), alice);
+        env.close();
+        auto USD = alice["USD"];
+
+        // The largest valid STAmount of USD:
+        STAmount const maxUSD(
+            USD.issue(), STAmount::cMaxValue, STAmount::cMaxOffset);
+
+        // Create a hotwallet
+        Account const hw{"hw"};
+        env.fund(XRP(10000), hw);
+        env(trust(hw, maxUSD));
+        env.close();
+        env(pay(alice, hw, maxUSD));
+
+        // Create some clients
+        Account const bob{"bob"};
+        env.fund(XRP(10000), bob);
+        env(trust(bob, maxUSD));
+        env.close();
+        env(pay(alice, bob, maxUSD));
+
+        Account const charley{"charley"};
+        env.fund(XRP(10000), charley);
+        env(trust(charley, maxUSD));
+        env.close();
+        env(pay(alice, charley, maxUSD));
+
+        env.close();
+
+        auto wsc = makeWSClient(env.app().config());
+
+        Json::Value query;
+        query[jss::account] = alice.human();
+        query[jss::hotwallet] = hw.human();
+
+        // Note that the sum of bob's and charley's USD balances exceeds
+        // the amount that can be represented in an STAmount.  Nevertheless
+        // we get a valid "obligations" that shows the maximum valid
+        // STAmount.
+        auto jv = wsc->invoke("gateway_balances", query);
+        expect(jv[jss::status] == "success");
+        expect(jv[jss::result][jss::obligations]["USD"] == maxUSD.getText());
+    }
+
     void
     run() override
     {
         using namespace jtx;
         auto const sa = supported_amendments();
         testGWB(sa - featureFlowCross);
         testGWB(sa);
+
+        testGWBOverflow();
     }
 };
 
```
