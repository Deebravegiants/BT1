# [?] offers: avoid panic when truncating payer_note in UTF-8 code point

## Summary
Severity: Unknown
Chain: Bitcoin/Lightning
Component: lightningdevkit/rust-lightning
Published: 2025-04-23
Source: https://github.com/lightningdevkit/rust-lightning/commit/c625a42e37d7aabff87b2de8359cf25125c68595
Type: security-commit

## Details
offers: avoid panic when truncating payer_note in UTF-8 code point

`String::truncate` takes a byte index but panics if we split in the
middle of a UTF-8 codepoint. Sadly, in `InvoiceRequest::fields` we
want to tuncate the payer note to a maximum of 512 bytes, which may
be in the middle of a UTF-8 codepoint and can cause panic.

Here we iterate over the bytes in the string until we find one not
in the middle of a UTF-8 codepoint and then split the string there.

## Patch
### lightning/src/offers/invoice_request.rs
```diff
@@ -998,15 +998,37 @@ impl VerifiedInvoiceRequest {
 		InvoiceRequestFields {
 			payer_signing_pubkey: *payer_signing_pubkey,
 			quantity: *quantity,
-			payer_note_truncated: payer_note.clone().map(|mut s| {
-				s.truncate(PAYER_NOTE_LIMIT);
-				UntrustedString(s)
-			}),
+			payer_note_truncated: payer_note
+				.clone()
+				// Truncate the payer note to `PAYER_NOTE_LIMIT` bytes, rounding
+				// down to the nearest valid UTF-8 code point boundary.
+				.map(|s| UntrustedString(string_truncate_safe(s, PAYER_NOTE_LIMIT))),
 			human_readable_name: self.offer_from_hrn().clone(),
 		}
 	}
 }
 
+/// `String::truncate(new_len)` panics if you split inside a UTF-8 code point,
+/// which would leave the `String` containing invalid UTF-8. This function will
+/// instead truncate the string to the next smaller code point boundary so the
+/// truncated string always remains valid UTF-8.
+///
+/// This can still split a grapheme cluster, but that's probably fine.
+/// We'd otherwise have to pull in the `unicode-segmentation` crate and its big
+/// unicode tables to find the next smaller grapheme cluster boundary.
+fn string_truncate_safe(mut s: String, new_len: usize) -> String {
+	// Finds the largest byte index `x` not exceeding byte index `index` where
+	// `s.is_char_boundary(x)` is true.
+	// TODO(phlip9): remove when `std::str::floor_char_boundary` stabilizes.
+	let truncated_len = if new_len >= s.len() {
+		s.len()
+	} else {
+		(0..=new_len).rev().find(|idx| s.is_char_boundary(*idx)).unwrap_or(0)
+	};
+	s.truncate(truncated_len);
+	s
+}
+
 impl InvoiceRequestContents {
 	pub(super) fn metadata(&self) -> &[u8] {
 		self.inner.metadata()
@@ -1426,6 +1448,7 @@ mod tests {
 	use crate::ln::inbound_payment::ExpandedKey;
 	use crate::ln::msgs::{DecodeError, MAX_VALUE_MSAT};
 	use crate::offers::invoice::{Bolt12Invoice, SIGNATURE_TAG as INVOICE_SIGNATURE_TAG};
+	use crate::offers::invoice_request::string_truncate_safe;
 	use crate::offers::merkle::{self, SignatureTlvStreamRef, TaggedHash, TlvStream};
 	use crate::offers::nonce::Nonce;
 	#[cfg(not(c_bindings))]
@@ -2947,14 +2970,20 @@ mod tests {
 			.unwrap();
 		assert_eq!(offer.issuer_signing_pubkey(), Some(node_id));
 
+		// UTF-8 payer note that we can't naively `.truncate(PAYER_NOTE_LIMIT)`
+		// because it would split a multi-byte UTF-8 code point.
+		let payer_note = "❤️".repeat(86);
+		assert_eq!(payer_note.len(), PAYER_NOTE_LIMIT + 4);
+		let expected_payer_note = "❤️".repeat(85);
+
 		let invoice_request = offer
 			.request_invoice(&expanded_key, nonce, &secp_ctx, payment_id)
 			.unwrap()
 			.chain(Network::Testnet)
 			.unwrap()
 			.quantity(1)
 			.unwrap()
-			.payer_note("0".repeat(PAYER_NOTE_LIMIT * 2))
+			.payer_note(payer_note)
 			.build_and_sign()
 			.unwrap();
 		match invoice_request.verify_using_metadata(&expanded_key, &secp_ctx) {
@@ -2966,7 +2995,7 @@ mod tests {
 					InvoiceRequestFields {
 						payer_signing_pubkey: invoice_request.payer_signing_pubkey(),
 						quantity: Some(1),
-						payer_note_truncated: Some(UntrustedString("0".repeat(PAYER_NOTE_LIMIT))),
+						payer_note_truncated: Some(UntrustedString(expected_payer_note)),
 						human_readable_name: None,
 					}
 				);
@@ -2981,4 +3010,31 @@ mod tests {
 			Err(_) => panic!("unexpected error"),
 		}
 	}
+
+	#[test]
+	fn test_string_truncate_safe() {
+		// We'll correctly truncate to the nearest UTF-8 code point boundary:
+		// ❤      variation-selector
+		// e29da4 efb88f
+		let s = String::from("❤️");
+		assert_eq!(s.len(), 6);
+		assert_eq!(s, string_truncate_safe(s.clone(), 7));
+		assert_eq!(s, string_truncate_safe(s.clone(), 6));
+		assert_eq!("❤", string_truncate_safe(s.clone(), 5));
+		assert_eq!("❤", string_truncate_safe(s.clone(), 4));
+		assert_eq!("❤", string_truncate_safe(s.clone(), 3));
+		assert_eq!("", string_truncate_safe(s.clone(), 2));
+		assert_eq!("", string_truncate_safe(s.clone(), 1));
+		assert_eq!("", string_truncate_safe(s.clone(), 0));
+
+		// Every byte in an ASCII string is also a full UTF-8 code point.
+		let s = String::from("my ASCII string!");
+		for new_len in 0..(s.len() + 5) {
+			if new_len >= s.len() {
+				assert_eq!(s, string_truncate_safe(s.clone(), new_len));
+			} else {
+				assert_eq!(s[..new_len], string_truncate_safe(s.clone(), new_len));
+			}
+		}
+	}
 }
```
