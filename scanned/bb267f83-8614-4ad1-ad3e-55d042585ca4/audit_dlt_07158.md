# [?] bolt12: cover the amount overflow guard

## Summary
Severity: Unknown
Chain: Bitcoin/Lightning
Component: lightningnetwork/lnd
Published: 2026-09-10
Source: https://github.com/lightningnetwork/lnd/commit/3c8e2bcba0f67b748c080fe4be552a6a7f0732f8
Type: security-commit

## Details
bolt12: cover the amount overflow guard

The request side had a test for the offer_amount times quantity overflow, the
invoice side did not, and it was the only uncovered branch in the invoice
amount check. Verified by neutering the guard, which makes the new case accept
an invoice_amount of one against an authorized amount that wrapped to zero.

Finding F9.
https://github.com/lightningnetwork/lnd/pull/10941#discussion_r3599755895

## Patch
### bolt12/validate_test.go
```diff
@@ -2052,6 +2052,53 @@ func TestValidateInvoiceRequestAmountOverflow(t *testing.T) {
 	require.ErrorIs(t, writeErr, ErrAmountBelowExpected)
 }
 
+// TestValidateInvoiceAmountOverflow is the invoice-side twin of
+// TestValidateInvoiceRequestAmountOverflow: with invreq_amount absent the
+// authorized amount is offer_amount times invreq_quantity, and that product
+// must not wrap. An unguarded multiply would truncate to zero and accept any
+// invoice_amount as "at least zero".
+func TestValidateInvoiceAmountOverflow(t *testing.T) {
+	t.Parallel()
+
+	_, pub := bobKey()
+
+	req := &InvoiceRequest{}
+	req.OfferIssuerID = tlv.SomeRecordT(
+		tlv.NewPrimitiveRecord[tlv.TlvType22](pub),
+	)
+	req.OfferAmount = tlv.SomeRecordT(
+		tlv.NewRecordT[tlv.TlvType8](TUint64(2)),
+	)
+
+	// quantity_max zero means unlimited, so the bound check does not cap
+	// the quantity below.
+	req.OfferQuantityMax = tlv.SomeRecordT(
+		tlv.NewRecordT[tlv.TlvType20](TUint64(0)),
+	)
+
+	// We request to pay 2^63 units, which would overflow the uint64 product
+	// with offer_amount(2).
+	req.InvreqQuantity = tlv.SomeRecordT(
+		tlv.NewRecordT[tlv.TlvType86](TUint64(1 << 63)),
+	)
+	req.InvreqPayerID = tlv.SomeRecordT(
+		tlv.NewPrimitiveRecord[tlv.TlvType88](pub),
+	)
+	req.InvreqMetadata = tlv.SomeRecordT(
+		tlv.NewPrimitiveRecord[tlv.TlvType0](tlv.Blob("m")),
+	)
+
+	// An invoice setting the overflow value of 0 would be accepted by an
+	// unguarded validator.
+	inv := NewInvoiceFromRequest(req)
+	inv.InvoiceAmount = tlv.SomeRecordT(
+		tlv.NewRecordT[tlv.TlvType170](TUint64(0)),
+	)
+
+	err := ValidateInvoiceAgainstRequest(inv, req)
+	require.ErrorIs(t, err, ErrAmountBelowExpected)
+}
+
 // TestValidateInvoiceRequestReadChain pins the spec invreq_chain rule:
 // an absent invreq_chain defaults to Bitcoin mainnet and must be
 // rejected on a non-mainnet node, while a present invreq_chain that
```
