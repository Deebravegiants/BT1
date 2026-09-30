# [?] Fix underflow rounding issue:

## Summary
Severity: Unknown
Chain: XRP
Component: XRPLF/rippled
Published: 2015-11-04
Source: https://github.com/XRPLF/rippled/commit/999701e3840dbfde1a75452a8e5a4d53a299535e
Type: security-commit

## Details
Fix underflow rounding issue:

Very small payment could fail when STAmount::mulRound underflowed
and returned zero, when it should have rounded up to the smallest
representable value.

## Patch
### src/ripple/app/paths/cursor/DeliverNodeForward.cpp
```diff
@@ -43,6 +43,9 @@ TER PathCursor::deliverNodeForward (
     // Zeroed in reverse pass.
     node().directory.restart(multiQuality_);
 
+    STAmountCalcSwitchovers amountCalcSwitchovers (
+        rippleCalc_.view.info ().parentCloseTime);
+
     saInAct.clear (saInReq);
     saInFees.clear (saInReq);
 
@@ -107,11 +110,11 @@ TER PathCursor::deliverNodeForward (
                 saOutPassFunded,
                 node().saOfrRate,
                 node().saTakerPays.issue (),
-                true);
+                true, amountCalcSwitchovers);
 
             // Offer maximum in with fees.
             auto saInTotal = mulRound (saInFunded, saInFeeRate,
-                saInFunded.issue (), true);
+                saInFunded.issue (), true, amountCalcSwitchovers);
             auto saInRemaining = saInReq - saInAct - saInFees;
 
             if (saInRemaining < zero)
@@ -123,11 +126,13 @@ TER PathCursor::deliverNodeForward (
             // In without fees.
             auto saInPassAct = std::min (
                 node().saTakerPays, divRound (
-                    saInSum, saInFeeRate, saInSum.issue (), true));
+                    saInSum, saInFeeRate, saInSum.issue (), true,
+                        amountCalcSwitchovers));
 
             // Out limited by in remaining.
             auto outPass = divRound (
-                saInPassAct, node().saOfrRate, node().saTakerGets.issue (), true);
+                saInPassAct, node().saOfrRate, node().saTakerGets.issue (), true,
+                amountCalcSwitchovers);
             STAmount saOutPassMax    = std::min (saOutPassFunded, outPass);
 
             STAmount saInPassFeesMax = saInSum - saInPassAct;
@@ -243,10 +248,12 @@ TER PathCursor::deliverNodeForward (
 
                     assert (saOutPassAct < saOutPassMax);
                     auto inPassAct = mulRound (
-                        saOutPassAct, node().saOfrRate, saInReq.issue (), true);
+                        saOutPassAct, node().saOfrRate, saInReq.issue (), true,
+                        amountCalcSwitchovers);
                     saInPassAct = std::min (node().saTakerPays, inPassAct);
                     auto inPassFees = mulRound (
-                        saInPassAct, saInFeeRate, saInPassAct.issue (), true);
+                        saInPassAct, saInFeeRate, saInPassAct.issue (), true,
+                        amountCalcSwitchovers);
                     saInPassFees    = std::min (saInPassFeesMax, inPassFees);
                 }
 
```

### src/ripple/app/paths/cursor/DeliverNodeReverse.cpp
```diff
@@ -45,6 +45,9 @@ TER PathCursor::deliverNodeReverseImpl (
 {
     TER resultCode   = tesSUCCESS;
 
+    STAmountCalcSwitchovers amountCalcSwitchovers (
+        rippleCalc_.view.info ().parentCloseTime);
+
     // Accumulation of what the previous node must deliver.
     // Possible optimization: Note this gets zeroed on each increment, ideally
     // only on first increment, then it could be a limit on the forward pass.
@@ -157,7 +160,10 @@ TER PathCursor::deliverNodeReverseImpl (
         //
         // Round down: prefer liquidity rather than microscopic fees.
         STAmount saOutPlusFees   = mulRound (
-            saOutPassAct, saOutFeeRate, saOutPassAct.issue (), false);
+            saOutPassAct, saOutFeeRate, saOutPassAct.issue (), false,
+            amountCalcSwitchovers);
+
+
         // Offer out with fees.
 
         JLOG (j_.trace)
@@ -178,7 +184,7 @@ TER PathCursor::deliverNodeReverseImpl (
             // Round up: prefer liquidity rather than microscopic fees. But,
             // limit by requested.
             auto fee = divRound (saOutPlusFees, saOutFeeRate,
-                saOutPlusFees.issue (), true);
+                saOutPlusFees.issue (), true, amountCalcSwitchovers);
             saOutPassAct = std::min (saOutPassReq, fee);
 
             JLOG (j_.trace)
@@ -190,7 +196,16 @@ TER PathCursor::deliverNodeReverseImpl (
 
         // Compute portion of input needed to cover actual output.
         auto outputFee = mulRound (
-            saOutPassAct, node().saOfrRate, node().saTakerPays.issue (), true);
+            saOutPassAct, node().saOfrRate, node().saTakerPays.issue (), true,
+            amountCalcSwitchovers);
+        if (!amountCalcSwitchovers.enableUnderflowFix () && !outputFee)
+        {
+            JLOG (j_.fatal)
+                << "underflow computing outputFee "
+                << "saOutPassAct: " << saOutPassAct
+                << " saOfrRate: " << node ().saOfrRate;
+            return telFAILED_PROCESSING;
+        }
         STAmount saInPassReq = std::min (node().saTakerPays, outputFee);
         STAmount saInPassAct;
 
@@ -255,10 +270,12 @@ TER PathCursor::deliverNodeReverseImpl (
         {
             // Adjust output to conform to limited input.
             auto outputRequirements = divRound (
-                saInPassAct, node().saOfrRate, node().saTakerGets.issue (), true);
+                saInPassAct, node ().saOfrRate, node ().saTakerGets.issue (), true,
+                amountCalcSwitchovers);
             saOutPassAct = std::min (saOutPassReq, outputRequirements);
             auto outputFees = mulRound (
-                saOutPassAct, saOutFeeRate, saOutPassAct.issue (), true);
+                saOutPassAct, saOutFeeRate, saOutPassAct.issue (), true,
+                amountCalcSwitchovers);
             saOutPlusFees   = std::min (node().saOfferFunds, outputFees);
 
             JLOG (j_.trace)
```

### src/ripple/app/paths/cursor/ForwardLiquidityForAccount.cpp
```diff
@@ -150,6 +150,9 @@ TER PathCursor::forwardLiquidityForAccount () const
                 << " previousNode.saFwdRedeem:" << previousNode().saFwdRedeem
                 << " previousNode.saFwdIssue:" << previousNode().saFwdIssue;
 
+            STAmountCalcSwitchovers amountCalcSwitchovers (
+                rippleCalc_.view.info ().parentCloseTime);
+
             // Last node. Accept all funds. Calculate amount actually to credit.
 
             auto& saCurReceive = pathState_.outPass();
@@ -159,7 +162,7 @@ TER PathCursor::forwardLiquidityForAccount () const
                           previousNode().saFwdIssue,
                           amountFromRate (uQualityIn),
                           previousNode().saFwdIssue.issue (),
-                          true); // Amount to credit.
+                          true, amountCalcSwitchovers); // Amount to credit.
 
             // Amount to credit. Credit for less than received as a surcharge.
             pathState_.setOutPass (previousNode().saFwdRedeem + saIssueCrd);
```

### src/ripple/app/paths/cursor/RippleLiquidity.cpp
```diff
@@ -135,16 +135,21 @@ void rippleLiquidity (
         // If the next rate is at least as good as the current rate, process.
         if (!uRateMax || uRate <= uRateMax)
         {
+            STAmountCalcSwitchovers amountCalcSwitchovers (
+                rippleCalc.view.info ().parentCloseTime);
+
             auto currency = saCur.getCurrency ();
             auto uCurIssuerID = saCur.getIssuer ();
 
             // current actual = current request * (quality out / quality in).
             auto numerator = mulRound (
-                saCur, uQualityOut, {currency, uCurIssuerID}, true);
+                saCur, uQualityOut, {currency, uCurIssuerID}, true,
+                amountCalcSwitchovers);
             // True means "round up" to get best flow.
 
             STAmount saCurIn = divRound (
-                numerator, uQualityIn, {currency, uCurIssuerID}, true);
+                numerator, uQualityIn, {currency, uCurIssuerID}, true,
+                amountCalcSwitchovers);
 
             JLOG (rippleCalc.j_.trace)
                 << "rippleLiquidity:"
@@ -173,11 +178,13 @@ void rippleLiquidity (
 
                 Issue issue{currency, uCurIssuerID};
                 auto numerator = mulRound (
-                    saPrv, uQualityIn, issue, true);
+                    saPrv, uQualityIn, issue, true,
+                    amountCalcSwitchovers);
                 // A part of current. All of previous. (Cur is the driver
                 // variable.)
                 STAmount saCurOut = divRound (
-                    numerator, uQualityOut, issue, true);
+                    numerator, uQualityOut, issue, true,
+                    amountCalcSwitchovers);
 
                 JLOG (rippleCalc.j_.trace)
                     << "rippleLiquidity:4: saCurReq=" << saCurReq;
```

### src/ripple/app/tests/Offer.test.cpp
```diff
@@ -121,10 +121,49 @@ class Offer_test : public beast::unit_test::suite
         expect (isOffer (env, "alice", XRP (300), USD (100)) &&
             isOffer (env, "alice", XRP (400), USD (200)));
     }
+    void testTinyPayment ()
+    {
+        // Regression test for tiny payments
+        using namespace jtx;
+        auto const alice = Account ("alice");
+        auto const bob = Account ("bob");
+        auto const carol = Account ("carol");
+        auto const gw = Account ("gw");
+
+        auto const USD = gw["USD"];
+        auto const EUR = gw["EUR"];
+
+        Env env (*this);
+
+
+        env.fund (XRP (10000), alice, bob, carol, gw);
+        env.trust (USD (1000), alice, bob, carol);
+        env.trust (EUR (1000), alice, bob, carol);
+        env (pay (gw, alice, USD (100)));
+        env (pay (gw, carol, EUR (100)));
+
+        // Create more offers than the loop max count in DeliverNodeReverse
+        for (int i=0;i<101;++i)
+            env (offer (carol, USD (1), EUR (2)));
+
+        auto const switchoverTime = STAmountCalcSwitchovers::enableUnderflowFixCloseTime ();
+
+        for (auto timeDelta : {-10, 10}){
+            auto const closeTime = switchoverTime + timeDelta;
+            STAmountCalcSwitchovers switchover (closeTime);
+            env.close (NetClock::time_point (std::chrono::seconds (closeTime)));
+            // Will fail without the underflow fix
+            auto expectedResult = switchover.enableUnderflowFix () ?
+                    tesSUCCESS : tecPATH_PARTIAL;
+            env (pay ("alice", "bob", EUR (epsilon)), path (~EUR),
+                sendmax (USD (100)), ter (expectedResult));
+        }
+    }
     void run ()
     {
         testCanceledOffer ();
         testRmFundedOffer ();
+        testTinyPayment ();
     }
 };
 
```

### src/ripple/app/tests/Taker.test.cpp
```diff
@@ -84,7 +84,8 @@ class Taker_test : public beast::unit_test::suite
         cross (Amounts offer1, Quality quality1, Amounts offer2, Quality quality2)
         {
             /* check if composed quality should be rejected */
-            Quality const quality (composed_quality (quality1, quality2));
+            Quality const quality (composed_quality (
+                quality1, quality2, STAmountCalcSwitchovers{false}));
 
             if (reject (quality))
                 return std::make_pair(
```

### src/ripple/app/tx/impl/CreateOffer.cpp
```diff
@@ -272,7 +272,8 @@ CreateOffer::dry_offer (ApplyView& view, Offer const& offer)
 std::pair<bool, Quality>
 CreateOffer::select_path (
     bool have_direct, OfferStream const& direct,
-    bool have_bridge, OfferStream const& leg1, OfferStream const& leg2)
+    bool have_bridge, OfferStream const& leg1, OfferStream const& leg2,
+    STAmountCalcSwitchovers const& amountCalcSwitchovers)
 {
     // If we don't have any viable path, why are we here?!
     assert (have_direct || have_bridge);
@@ -282,7 +283,7 @@ CreateOffer::select_path (
         return std::make_pair (true, direct.tip ().quality ());
 
     Quality const bridged_quality (composed_quality (
-        leg1.tip ().quality (), leg2.tip ().quality ()));
+        leg1.tip ().quality (), leg2.tip ().quality (), amountCalcSwitchovers));
 
     if (have_direct)
     {
@@ -349,6 +350,9 @@ CreateOffer::bridged_cross (
 
     auto viewJ = ctx_.app.journal ("View");
 
+    STAmountCalcSwitchovers amountCalcSwitchovers (
+        view.info ().parentCloseTime);
+
     // Modifying the order or logic of the operations in the loop will cause
     // a protocol breaking change.
     while (have_direct || have_bridge)
@@ -362,7 +366,9 @@ CreateOffer::bridged_cross (
 
         std::tie (use_direct, quality) = select_path (
             have_direct, offers_direct,
-            have_bridge, offers_leg1, offers_leg2);
+            have_bridge, offers_leg1, offers_leg2,
+            amountCalcSwitchovers);
+
 
         // We are always looking at the best quality; we are done with
         // crossing as soon as we cross the quality boundary.
@@ -465,7 +471,7 @@ CreateOffer::bridged_cross (
             Throw<std::logic_error> ("bridged crossing: nothing was fully consumed.");
     }
 
-    return std::make_pair(cross_result, taker.remaining_offer ());
+    return std::make_pair(cross_result, taker.remaining_offer (amountCalcSwitchovers));
 }
 
 std::pair<TER, Amounts>
@@ -546,7 +552,8 @@ CreateOffer::direct_cross (
             Throw<std::logic_error> ("direct crossing: nothing was fully consumed.");
     }
 
-    return std::make_pair(cross_result, taker.remaining_offer ());
+    STAmountCalcSwitchovers amountCalcSwitchovers (view.info ().parentCloseTime);
+    return std::make_pair(cross_result, taker.remaining_offer (amountCalcSwitchovers));
 }
 
 // Step through the stream for as long as possible, skipping any offers
@@ -590,6 +597,7 @@ CreateOffer::cross (
     Taker taker (cross_type_, view, account_, taker_amount,
         ctx_.tx.getFlags(), beast::Journal (takerSink));
 
+    STAmountCalcSwitchovers amountCalcSwitchovers (view.info ().parentCloseTime);
     try
     {
         if (cross_type_ == CrossType::IouToIou)
@@ -600,7 +608,7 @@ CreateOffer::cross (
     catch (std::exception const& e)
     {
         j_.error << "Exception during offer crossing: " << e.what ();
-        return std::make_pair (tecINTERNAL, taker.remaining_offer ());
+        return std::make_pair (tecINTERNAL, taker.remaining_offer (amountCalcSwitchovers));
     }
 }
 
```

### src/ripple/app/tx/impl/CreateOffer.h
```diff
@@ -77,7 +77,8 @@ class CreateOffer
     std::pair<bool, Quality>
     select_path (
         bool have_direct, OfferStream const& direct,
-        bool have_bridge, OfferStream const& leg1, OfferStream const& leg2);
+        bool have_bridge, OfferStream const& leg1, OfferStream const& leg2,
+        STAmountCalcSwitchovers const& amountCalcSwitchovers);
 
     std::pair<TER, Amounts>
     bridged_cross (
```

### src/ripple/app/tx/impl/Taker.cpp
```diff
@@ -140,7 +140,7 @@ BasicTaker::done () const
 }
 
 Amounts
-BasicTaker::remaining_offer () const
+BasicTaker::remaining_offer (STAmountCalcSwitchovers const& amountCalcSwitchovers) const
 {
     // If the taker is done, then there's no offer to place.
     if (done ())
@@ -156,14 +156,16 @@ BasicTaker::remaining_offer () const
 
         // We scale the output based on the remaining input:
         return Amounts (remaining_.in, divRound (
-            remaining_.in, quality_.rate (), issue_out_, true));
+            remaining_.in, quality_.rate (), issue_out_, true,
+            amountCalcSwitchovers));
     }
 
     assert (remaining_.out > zero);
 
     // We scale the input based on the remaining output:
     return Amounts (mulRound (
-        remaining_.out, quality_.rate (), issue_in_, true), remaining_.out);
+        remaining_.out, quality_.rate (), issue_in_, true, amountCalcSwitchovers),
+        remaining_.out);
 }
 
 Amounts const&
```

### src/ripple/app/tx/impl/Taker.h
```diff
@@ -167,7 +167,7 @@ class BasicTaker
         It is always at the original offer quality (quality_)
     */
     Amounts
-    remaining_offer () const;
+    remaining_offer (STAmountCalcSwitchovers const& amountCalcSwitchovers) const;
 
     /** Returns the amount that the offer was originally placed at. */
     Amounts const&
```

### src/ripple/protocol/Quality.h
```diff
@@ -131,14 +131,16 @@ class Quality
         to prevent money creation.
     */
     Amounts
-    ceil_in (Amounts const& amount, STAmount const& limit) const;
+    ceil_in (Amounts const& amount, STAmount const& limit,
+             STAmountCalcSwitchovers const& switchovers) const;
 
     /** Returns the scaled amount with out capped.
         Math is avoided if the result is exact. The input is clamped
         to prevent money creation.
     */
     Amounts
-    ceil_out (Amounts const& amount, STAmount const& limit) const;
+    ceil_out (Amounts const& amount, STAmount const& limit,
+              STAmountCalcSwitchovers const& switchovers) const;
 
     /** Returns `true` if lhs is lower quality than `rhs`.
         Lower quality means the taker receives a worse deal.
@@ -179,7 +181,8 @@ class Quality
     @param rhs  The second leg of the path: intermediate to output.
 */
 Quality
-composed_quality (Quality const& lhs, Quality const& rhs);
+composed_quality (Quality const& lhs, Quality const& rhs,
+                  STAmountCalcSwitchovers const& switchovers);
 
 }
 
```

### src/ripple/protocol/STAmount.h
```diff
@@ -377,15 +377,32 @@ divide (STAmount const& v1, STAmount const& v2, Issue const& issue);
 STAmount
 multiply (STAmount const& v1, STAmount const& v2, Issue const& issue);
 
-// multiply, or divide rounding result in specified direction
+/** Control when bugfixes that require switchover dates are enabled */
+class STAmountCalcSwitchovers
+{
+    bool enableUnderflowFix_ {false};
+  public:
+    STAmountCalcSwitchovers () = delete;
+    explicit
+    STAmountCalcSwitchovers (std::uint32_t parentCloseTime);
+    explicit
+    STAmountCalcSwitchovers (bool enableAll)
+        : enableUnderflowFix_ (enableAll) {}
+    bool enableUnderflowFix () const;
+    // for tests
+    static std::uint32_t enableUnderflowFixCloseTime ();
+};
 
+// multiply, or divide rounding result in specified direction
 STAmount
 mulRound (STAmount const& v1, STAmount const& v2,
-    Issue const& issue, bool roundUp);
+    Issue const& issue, bool roundUp,
+        STAmountCalcSwitchovers const& switchovers);
 
 STAmount
 divRound (STAmount const& v1, STAmount const& v2,
-    Issue const& issue, bool roundUp);
+    Issue const& issue, bool roundUp,
+        STAmountCalcSwitchovers const& switchovers);
 
 // Someone is offering X for Y, what is the rate?
 // Rate: smaller is better, the taker wants the most out: in/out
```
