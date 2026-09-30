# [?] msggen: fix non-determinism edge case

## Summary
Severity: Unknown
Chain: Bitcoin/Lightning
Component: ElementsProject/lightning
Published: 2026-05-25
Source: https://github.com/ElementsProject/lightning/commit/11b83240389128c5bf7f6342734c2465f5ee995e
Type: security-commit

## Details
msggen: fix non-determinism edge case

After adding back some fields in 62d1e3e405f722e7363d8e8dbc427039a12c421a
there is one field that was in a different place sometimes in node.proto:
DecodeInvoicePathsPath

Changelog-None

## Patch
### cln-grpc/proto/node.proto
```diff
@@ -211,13 +211,6 @@ message GetinfoResponse {
 	optional string warning_lightningd_sync = 17;
 }
 
-message GetinfoOurFeatures {
-	bytes init = 1;
-	bytes node = 2;
-	bytes channel = 3;
-	bytes invoice = 4;
-}
-
 message GetinfoAddress {
 	// Getinfo.address[].type
 	enum GetinfoAddressType {
@@ -249,6 +242,13 @@ message GetinfoBinding {
 	optional string subtype = 5;
 }
 
+message GetinfoOurFeatures {
+	bytes init = 1;
+	bytes node = 2;
+	bytes channel = 3;
+	bytes invoice = 4;
+}
+
 message ListpeersRequest {
 	// ListPeers.level
 	enum ListpeersLevel {
@@ -306,6 +306,18 @@ message ListfundsResponse {
 	repeated ListfundsChannels channels = 2;
 }
 
+message ListfundsChannels {
+	bytes peer_id = 1;
+	Amount our_amount_msat = 2;
+	Amount amount_msat = 3;
+	bytes funding_txid = 4;
+	uint32 funding_output = 5;
+	bool connected = 6;
+	ChannelState state = 7;
+	optional string short_channel_id = 8;
+	bytes channel_id = 9;
+}
+
 message ListfundsOutputs {
 	// ListFunds.outputs[].status
 	enum ListfundsOutputsStatus {
@@ -326,18 +338,6 @@ message ListfundsOutputs {
 	optional uint32 reserved_to_block = 10;
 }
 
-message ListfundsChannels {
-	bytes peer_id = 1;
-	Amount our_amount_msat = 2;
-	Amount amount_msat = 3;
-	bytes funding_txid = 4;
-	uint32 funding_output = 5;
-	bool connected = 6;
-	ChannelState state = 7;
-	optional string short_channel_id = 8;
-	bytes channel_id = 9;
-}
-
 message SendpayRequest {
 	repeated SendpayRoute route = 1;
 	bytes payment_hash = 2;
@@ -456,7 +456,7 @@ message AutocleanonceAutoclean {
 	optional AutocleanonceAutocleanNetworkevents networkevents = 7;
 }
 
-message AutocleanonceAutocleanSucceededforwards {
+message AutocleanonceAutocleanExpiredinvoices {
 	uint64 cleaned = 1;
 	uint64 uncleaned = 2;
 }
@@ -466,12 +466,12 @@ message AutocleanonceAutocleanFailedforwards {
 	uint64 uncleaned = 2;
 }
 
-message AutocleanonceAutocleanSucceededpays {
+message AutocleanonceAutocleanFailedpays {
 	uint64 cleaned = 1;
 	uint64 uncleaned = 2;
 }
 
-message AutocleanonceAutocleanFailedpays {
+message AutocleanonceAutocleanNetworkevents {
 	uint64 cleaned = 1;
 	uint64 uncleaned = 2;
 }
@@ -481,12 +481,12 @@ message AutocleanonceAutocleanPaidinvoices {
 	uint64 uncleaned = 2;
 }
 
-message AutocleanonceAutocleanExpiredinvoices {
+message AutocleanonceAutocleanSucceededforwards {
 	uint64 cleaned = 1;
 	uint64 uncleaned = 2;
 }
 
-message AutocleanonceAutocleanNetworkevents {
+message AutocleanonceAutocleanSucceededpays {
 	uint64 cleaned = 1;
 	uint64 uncleaned = 2;
 }
@@ -509,7 +509,7 @@ message AutocleanstatusAutoclean {
 	optional AutocleanstatusAutocleanNetworkevents networkevents = 7;
 }
 
-message AutocleanstatusAutocleanSucceededforwards {
+message AutocleanstatusAutocleanExpiredinvoices {
 	bool enabled = 1;
 	uint64 cleaned = 2;
 	optional uint64 age = 3;
@@ -521,13 +521,13 @@ message AutocleanstatusAutocleanFailedforwards {
 	optional uint64 age = 3;
 }
 
-message AutocleanstatusAutocleanSucceededpays {
+message AutocleanstatusAutocleanFailedpays {
 	bool enabled = 1;
 	uint64 cleaned = 2;
 	optional uint64 age = 3;
 }
 
-message AutocleanstatusAutocleanFailedpays {
+message AutocleanstatusAutocleanNetworkevents {
 	bool enabled = 1;
 	uint64 cleaned = 2;
 	optional uint64 age = 3;
@@ -539,13 +539,13 @@ message AutocleanstatusAutocleanPaidinvoices {
 	optional uint64 age = 3;
 }
 
-message AutocleanstatusAutocleanExpiredinvoices {
+message AutocleanstatusAutocleanSucceededforwards {
 	bool enabled = 1;
 	uint64 cleaned = 2;
 	optional uint64 age = 3;
 }
 
-message AutocleanstatusAutocleanNetworkevents {
+message AutocleanstatusAutocleanSucceededpays {
 	bool enabled = 1;
 	uint64 cleaned = 2;
 	optional uint64 age = 3;
@@ -1000,17 +1000,17 @@ message SendonionFirstHop {
 }
 
 message ListsendpaysRequest {
+	// ListSendPays.index
+	enum ListsendpaysIndex {
+		CREATED = 0;
+		UPDATED = 1;
+	}
 	// ListSendPays.status
 	enum ListsendpaysStatus {
 		PENDING = 0;
 		COMPLETE = 1;
 		FAILED = 2;
 	}
-	// ListSendPays.index
-	enum ListsendpaysIndex {
-		CREATED = 0;
-		UPDATED = 1;
-	}
 	optional string bolt11 = 1;
 	optional bytes payment_hash = 2;
 	optional ListsendpaysStatus status = 3;
@@ -1141,15 +1141,6 @@ message ListnodesNodes {
 	optional ListnodesNodesOptionWillFund option_will_fund = 7;
 }
 
-message ListnodesNodesOptionWillFund {
-	Amount lease_fee_base_msat = 1;
-	uint32 lease_fee_basis = 2;
-	uint32 funding_weight = 3;
-	Amount channel_fee_max_base_msat = 4;
-	uint32 channel_fee_max_proportional_thousandths = 5;
-	bytes compact_lease = 6;
-}
-
 message ListnodesNodesAddresses {
 	// ListNodes.nodes[].addresses[].type
 	enum ListnodesNodesAddressesType {
@@ -1164,6 +1155,15 @@ message ListnodesNodesAddresses {
 	optional string address = 3;
 }
 
+message ListnodesNodesOptionWillFund {
+	Amount lease_fee_base_msat = 1;
+	uint32 lease_fee_basis = 2;
+	uint32 funding_weight = 3;
+	Amount channel_fee_max_base_msat = 4;
+	uint32 channel_fee_max_proportional_thousandths = 5;
+	bytes compact_lease = 6;
+}
+
 message WaitanyinvoiceRequest {
 	optional uint64 lastpay_index = 1;
 	optional uint64 timeout = 2;
@@ -1502,47 +1502,21 @@ message ListpeerchannelsChannels {
 	repeated string features = 63;
 }
 
+message ListpeerchannelsChannelsAlias {
+	optional string local = 1;
+	optional string remote = 2;
+}
+
 message ListpeerchannelsChannelsChannelType {
 	repeated uint32 bits = 1;
 	repeated ChannelTypeName names = 2;
 }
 
-message ListpeerchannelsChannelsUpdates {
-	ListpeerchannelsChannelsUpdatesLocal local = 1;
-	optional ListpeerchannelsChannelsUpdatesRemote remote = 2;
-}
-
-message ListpeerchannelsChannelsUpdatesLocal {
-	Amount htlc_minimum_msat = 1;
-	Amount htlc_maximum_msat = 2;
-	uint32 cltv_expiry_delta = 3;
-	Amount fee_base_msat = 4;
-	uint32 fee_proportional_millionths = 5;
-}
-
-message ListpeerchannelsChannelsUpdatesRemote {
-	Amount htlc_minimum_msat = 1;
-	Amount htlc_maximum_msat = 2;
-	uint32 cltv_expiry_delta = 3;
-	Amount fee_base_msat = 4;
-	uint32 fee_proportional_millionths = 5;
-}
-
 message ListpeerchannelsChannelsFeerate {
 	uint32 perkw = 1;
 	uint32 perkb = 2;
 }
 
-message ListpeerchannelsChannelsInflight {
-	bytes funding_txid = 1;
-	uint32 funding_outnum = 2;
-	string feerate = 3;
-	Amount total_funding_msat = 4;
-	Amount our_funding_msat = 5;
-	optional bytes scratch_txid = 6;
-	sint64 splice_amount = 7;
-}
-
 message ListpeerchannelsChannelsFunding {
 	optional Amount pushed_msat = 1;
 	Amount local_funds_msat = 2;
@@ -1553,9 +1527,30 @@ message ListpeerchannelsChannelsFunding {
 	optional bool withheld = 7;
 }
 
-message ListpeerchannelsChannelsAlias {
-	optional string local = 1;
-	optional string remote = 2;
+message ListpeerchannelsChannelsHtlcs {
+	// ListPeerChannels.channels[].htlcs[].direction
+	enum ListpeerchannelsChannelsHtlcsDirection {
+		IN = 0;
+		OUT = 1;
+	}
+	ListpeerchannelsChannelsHtlcsDirection direction = 1;
+	uint64 id = 2;
+	Amount amount_msat = 3;
+	uint32 expiry = 4;
+	bytes payment_hash = 5;
+	optional bool local_trimmed = 6;
+	optional string status = 7;
+	HtlcState state = 8;
+}
+
+message ListpeerchannelsChannelsInflight {
+	bytes funding_txid = 1;
+	uint32 funding_outnum = 2;
+	string feerate = 3;
+	Amount total_funding_msat = 4;
+	Amount our_funding_msat = 5;
+	optional bytes scratch_txid = 6;
+	sint64 splice_amount = 7;
 }
 
 message ListpeerchannelsChannelsStateChanges {
@@ -1575,20 +1570,25 @@ message ListpeerchannelsChannelsStateChanges {
 	string message = 5;
 }
 
-message ListpeerchannelsChannelsHtlcs {
-	// ListPeerChannels.channels[].htlcs[].direction
-	enum ListpeerchannelsChannelsHtlcsDirection {
-		IN = 0;
-		OUT = 1;
-	}
-	ListpeerchannelsChannelsHtlcsDirection direction = 1;
-	uint64 id = 2;
-	Amount amount_msat = 3;
-	uint32 expiry = 4;
-	bytes payment_hash = 5;
-	optional bool local_trimmed = 6;
-	optional string status = 7;
-	HtlcState state = 8;
+message ListpeerchannelsChannelsUpdates {
+	ListpeerchannelsChannelsUpdatesLocal local = 1;
+	optional ListpeerchannelsChannelsUpdatesRemote remote = 2;
+}
+
+message ListpeerchannelsChannelsUpdatesLocal {
+	Amount htlc_minimum_msat = 1;
+	Amount htlc_maximum_msat = 2;
+	uint32 cltv_expiry_delta = 3;
+	Amount fee_base_msat = 4;
+	uint32 fee_proportional_millionths = 5;
+}
+
+message ListpeerchannelsChannelsUpdatesRemote {
+	Amount htlc_minimum_msat = 1;
+	Amount htlc_maximum_msat = 2;
+	uint32 cltv_expiry_delta = 3;
+	Amount fee_base_msat = 4;
+	uint32 fee_proportional_millionths = 5;
 }
 
 message ListclosedchannelsRequest {
@@ -1761,6 +1761,72 @@ message DecodeResponse {
 	repeated DecodeUnknownPayerProofTlvs unknown_payer_proof_tlvs = 99;
 }
 
+message DecodeExtra {
+	string tag = 1;
+	string data = 2;
+}
+
+message DecodeFallbacks {
+	// Decode.fallbacks[].type
+	enum DecodeFallbacksType {
+		P2PKH = 0;
+		P2SH = 1;
+		P2WPKH = 2;
+		P2WSH = 3;
+		P2TR = 4;
+	}
+	DecodeFallbacksType item_type = 2;
+	optional string addr = 3;
+	bytes hex = 4;
+}
+
+message DecodeInvoiceFallbacks {
+	uint32 version = 1;
+	bytes hex = 2;
+	optional string address = 3;
+}
+
+message DecodeInvoicePaths {
+	repeated DecodeInvoicePathsPath path = 1;
+	DecodeInvoicePathsPayinfo payinfo = 2;
+	optional bytes first_node_id = 3;
+	optional bytes first_path_key = 4;
+	optional uint32 first_scid_dir = 5;
+	optional string first_scid = 6;
+}
+
+message DecodeInvoicePathsPath {
+	bytes blinded_node_id = 1;
+	bytes encrypted_recipient_data = 2;
+}
+
+message DecodeInvoicePathsPayinfo {
+	optional Amount htlc_minimum_msat = 1;
+	bytes features = 2;
+	Amount fee_base_msat = 3;
+	uint32 fee_proportional_millionths = 4;
+	optional Amount htlc_maximum_msat = 5;
+	uint32 cltv_expiry_delta = 6;
+}
+
+message DecodeInvreqBip353Name {
+	optional string name = 1;
+	optional string domain = 2;
+}
+
+message DecodeInvreqPaths {
+	optional uint32 first_scid_dir = 1;
+	optional bytes first_node_id = 3;
+	optional string first_scid = 4;
+	repeated DecodeInvreqPathsPath path = 5;
+	optional bytes first_path_key = 6;
+}
+
+message DecodeInvreqPathsPath {
+	bytes blinded_node_id = 1;
+	bytes encrypted_recipient_data = 2;
+}
+
 message DecodeOfferPaths {
 	optional bytes first_node_id = 1;
 	repeated DecodeOfferPathsPath path = 3;
@@ -1790,101 +1856,35 @@ message DecodeOfferRecurrencePaywindow {
 	optional bool proportional_amount = 3;
 }
 
-message DecodeUnknownOfferTlvs {
+message DecodeRestrictions {
+	repeated string alternatives = 1;
+	string summary = 2;
+}
+
+message DecodeUnknownInvoiceRequestTlvs {
 	uint64 item_type = 1;
 	uint64 length = 2;
 	bytes value = 3;
 }
 
-message DecodeInvreqPaths {
-	optional uint32 first_scid_dir = 1;
-	optional bytes first_node_id = 3;
-	optional string first_scid = 4;
-	repeated DecodeInvreqPathsPath path = 5;
-	optional bytes first_path_key = 6;
-}
-
-message DecodeInvreqPathsPath {
-	bytes blinded_node_id = 1;
-	bytes encrypted_recipient_data = 2;
-}
-
-message DecodeInvreqBip353Name {
-	optional string name = 1;
-	optional string domain = 2;
-}
-
-message DecodeUnknownInvoiceRequestTlvs {
+message DecodeUnknownInvoiceTlvs {
 	uint64 item_type = 1;
 	uint64 length = 2;
 	bytes value = 3;
 }
 
-message DecodeInvoicePaths {
-	repeated DecodeInvoicePathsPath path = 1;
-	DecodeInvoicePathsPayinfo payinfo = 2;
-	optional bytes first_node_id = 3;
-	optional bytes first_path_key = 4;
-	optional uint32 first_scid_dir = 5;
-	optional string first_scid = 6;
-}
-
-message DecodeInvoicePathsPath {
-	bytes blinded_node_id = 1;
-	bytes encrypted_recipient_data = 2;
-}
-
-message DecodeInvoicePathsPayinfo {
-	optional Amount htlc_minimum_msat = 1;
-	bytes features = 2;
-	Amount fee_base_msat = 3;
-	uint32 fee_proportional_millionths = 4;
-	optional Amount htlc_maximum_msat = 5;
-	uint32 cltv_expiry_delta = 6;
-}
-
-message DecodeInvoiceFallbacks {
-	uint32 version = 1;
-	bytes hex = 2;
-	optional string address = 3;
-}
-
-message DecodeUnknownInvoiceTlvs {
+message DecodeUnknownOfferTlvs {
 	uint64 item_type = 1;
 	uint64 length = 2;
 	bytes value = 3;
 }
 
-message DecodeFallbacks {
-	// Decode.fallbacks[].type
-	enum DecodeFallbacksType {
-		P2PKH = 0;
-		P2SH = 1;
-		P2WPKH = 2;
-		P2WSH = 3;
-		P2TR = 4;
-	}
-	DecodeFallbacksType item_type = 2;
-	optional string addr = 3;
-	bytes hex = 4;
-}
-
-message DecodeExtra {
-	string tag = 1;
-	string data = 2;
-}
-
 message DecodeUnknownPayerProofTlvs {
 	uint64 item_type = 1;
 	uint64 length = 2;
 	bytes value = 3;
 }
 
-message DecodeRestrictions {
-	repeated string alternatives = 1;
-	string summary = 2;
-}
-
 message DelpayRequest {
 	// DelPay.status
 	enum DelpayStatus {
@@ -1996,6 +1996,15 @@ message FeeratesResponse {
 	optional FeeratesOnchainFeeEstimates onchain_fee_estimates = 4;
 }
 
+message FeeratesOnchainFeeEstimates {
+	uint64 opening_channel_satoshis = 1;
+	uint64 mutual_close_satoshis = 2;
+	uint64 unilateral_close_satoshis = 3;
+	uint64 htlc_timeout_satoshis = 4;
+	uint64 htlc_success_satoshis = 5;
+	optional uint64 unilateral_close_nonanchor_satoshis = 6;
+}
+
 message FeeratesPerkb {
 	uint32 min_acceptable = 1;
 	uint32 max_acceptable = 2;
@@ -2034,15 +2043,6 @@ message FeeratesPerkwEstimates {
 	uint32 smoothed_feerate = 3;
 }
 
-message FeeratesOnchainFeeEstimates {
-	uint64 opening_channel_satoshis = 1;
-	uint64 mutual_close_satoshis = 2;
-	uint64 unilateral_close_satoshis = 3;
-	uint64 htlc_timeout_satoshis = 4;
-	uint64 htlc_success_satoshis = 5;
-	optional uint64 unilateral_close_nonanchor_satoshis = 6;
-}
-
 message Fetchbip353Request {
 	string address = 1;
 }
@@ -2321,18 +2321,18 @@ message ListaddressesAddresses {
 }
 
 message ListforwardsRequest {
+	// ListForwards.index
+	enum ListforwardsIndex {
+		CREATED = 0;
+		UPDATED = 1;
+	}
 	// ListForwards.status
 	enum ListforwardsStatus {
 		OFFERED = 0;
 		SETTLED = 1;
 		LOCAL_FAILED = 2;
 		FAILED = 3;
 	}
-	// ListForwards.index
-	enum ListforwardsIndex {
-		CREATED = 0;
-		UPDATED = 1;
-	}
 	optional ListforwardsStatus status = 1;
 	optional string in_channel = 2;
 	optional string out_channel = 3;
@@ -2396,17 +2396,17 @@ message ListoffersOffers {
 }
 
 message ListpaysRequest {
+	// ListPays.index
+	enum ListpaysIndex {
+		CREATED = 0;
+		UPDATED = 1;
+	}
 	// ListPays.status
 	enum ListpaysStatus {
 		PENDING = 0;
 		COMPLETE = 1;
 		FAILED = 2;
 	}
-	// ListPays.index
-	enum ListpaysIndex {
-		CREATED = 0;
-		UPDATED = 1;
-	}
 	optional string bolt11 = 1;
 	optional bytes payment_hash = 2;
 	optional ListpaysStatus status = 3;
@@ -3004,6 +3004,12 @@ message WaitblockheightResponse {
 }
 
 message WaitRequest {
+	// Wait.indexname
+	enum WaitIndexname {
+		CREATED = 0;
+		UPDATED = 1;
+		DELETED = 2;
+	}
 	// Wait.subsystem
 	enum WaitSubsystem {
 		INVOICES = 0;
@@ -3014,12 +3020,6 @@ message WaitRequest {
 		CHANNELMOVES = 5;
 		NETWORKEVENTS = 6;
 	}
-	// Wait.indexname
-	enum WaitIndexname {
-		CREATED = 0;
-		UPDATED = 1;
-		DELETED = 2;
-	}
 	WaitSubsystem subsystem = 1;
 	WaitIndexname indexname = 2;
 	uint64 nextvalue = 3;
@@ -3050,6 +3050,45 @@ message WaitResponse {
 	optional WaitNetworkevents networkevents = 12;
 }
 
+message WaitChainmoves {
+	string account = 1;
+	Amount credit_msat = 2;
+	Amount debit_msat = 3;
+}
+
+message WaitChannelmoves {
+	string account = 1;
+	Amount credit_msat = 2;
+	Amount debit_msat = 3;
+}
+
+message WaitDetails {
+	// Wait.details.status
+	enum WaitDetailsStatus {
+		UNPAID = 0 [deprecated = true];
+		PAID = 1 [deprecated = true];
+		EXPIRED = 2 [deprecated = true];
+		PENDING = 3 [deprecated = true];
+		FAILED = 4 [deprecated = true];
+		COMPLETE = 5 [deprecated = true];
+		OFFERED = 6 [deprecated = true];
+		SETTLED = 7 [deprecated = true];
+		LOCAL_FAILED = 8 [deprecated = true];
+	}
+	optional WaitDetailsStatus status = 1 [deprecated = true];
+	optional string label = 2 [deprecated = true];
+	optional string description = 3 [deprecated = true];
+	optional string bolt11 = 4 [deprecated = true];
+	optional string bolt12 = 5 [deprecated = true];
+	optional uint64 partid = 6 [deprecated = true];
+	optional uint64 groupid = 7 [deprecated = true];
+	optional bytes payment_hash = 8 [deprecated = true];
+	optional string in_channel = 9 [deprecated = true];
+	optional uint64 in_htlc_id = 10 [deprecated = true];
+	optional Amount in_msat = 11 [deprecated = true];
+	optional string out_channel = 12 [deprecated = true];
+}
+
 message WaitForwards {
 	// Wait.forwards.status
 	enum WaitForwardsStatus {
@@ -3065,33 +3104,6 @@ message WaitForwards {
 	optional string out_channel = 5;
 }
 
-message WaitInvoices {
-	// Wait.invoices.status
-	enum WaitInvoicesStatus {
-		UNPAID = 0;
-		PAID = 1;
-		EXPIRED = 2;
-	}
-	optional WaitInvoicesStatus status = 1;
-	optional string label = 2;
-	optional string description = 3;
-	optional string bolt11 = 4;
-	optional string bolt12 = 5;
-}
-
-message WaitSendpays {
-	// Wait.sendpays.status
-	enum WaitSendpaysStatus {
-		PENDING = 0;
-		FAILED = 1;
-		COMPLETE = 2;
-	}
-	optional WaitSendpaysStatus status = 1;
-	optional uint64 partid = 2;
-	optional uint64 groupid = 3;
-	optional bytes payment_hash = 4;
-}
-
 message WaitHtlcs {
 	// Wait.htlcs.direction
 	enum WaitHtlcsDirection {
@@ -3107,16 +3119,18 @@ message WaitHtlcs {
 	optional bytes payment_hash = 7;
 }
 
-message WaitChainmoves {
-	string account = 1;
-	Amount credit_msat = 2;
-	Amount debit_msat = 3;
-}
-
-message WaitChannelmoves {
-	string account = 1;
-	Amount credit_msat = 2;
-	Amount debit_msat = 3;
+message WaitInvoices {
+	// Wait.invoices.status
+	enum WaitInvoicesStatus {
+		UNPAID = 0;
+		PAID = 1;
+		EXPIRED = 2;
+	}
+	optional WaitInvoicesStatus status = 1;
+	optional string label = 2;
+	optional string description = 3;
+	optional string bolt11 = 4;
+	optional string bolt12 = 5;
 }
 
 message WaitNetworkevents {
@@ -3132,31 +3146,17 @@ message WaitNetworkevents {
 	optional bytes peer_id = 3;
 }
 
-message WaitDetails {
-	// Wait.details.status
-	enum WaitDetailsStatus {
-		UNPAID = 0 [deprecated = true];
-		PAID = 1 [deprecated = true];
-		EXPIRED = 2 [deprecated = true];
-		PENDING = 3 [deprecated = true];
-		FAILED = 4 [deprecated = true];
-		COMPLETE = 5 [deprecated = true];
-		OFFERED = 6 [deprecated = true];
-		SETTLED = 7 [deprecated = true];
-		LOCAL_FAILED = 8 [deprecated = true];
+message WaitSendpays {
+	// Wait.sendpays.status
+	enum WaitSendpaysStatus {
+		PENDING = 0;
+		FAILED = 1;
+		COMPLETE = 2;
 	}
-	optional WaitDetailsStatus status = 1 [deprecated = true];
-	optional string label = 2 [deprecated = true];
-	optional string description = 3 [deprecated = true];
-	optional string bolt11 = 4 [deprecated = true];
-	optional string bolt12 = 5 [deprecated = true];
-	optional uint64 partid = 6 [deprecated = true];
-	optional uint64 groupid = 7 [deprecated = true];
-	optional bytes payment_hash = 8 [deprecated = true];
-	optional string in_channel = 9 [deprecated = true];
-	optional uint64 in_htlc_id = 10 [deprecated = true];
-	optional Amount in_msat = 11 [deprecated = true];
-	optional string out_channel = 12 [deprecated = true];
+	optional WaitSendpaysStatus status = 1;
+	optional uint64 partid = 2;
+	optional uint64 groupid = 3;
+	optional bytes payment_hash = 4;
 }
 
 message ListconfigsRequest {
@@ -3239,364 +3239,364 @@ message ListconfigsConfigs {
 	optional ListconfigsConfigsCurrencyratedisablesource currencyrate_disable_source = 75;
 }
 
-message ListconfigsConfigsConf {
-	// ListConfigs.configs.conf.source
-	enum ListconfigsConfigsConfSource {
-		CMDLINE = 0;
-	}
-	string value_str = 1;
-	ListconfigsConfigsConfSource source = 2;
+message ListconfigsConfigsAddr {
+	repeated string values_str = 1;
+	repeated string sources = 2;
 }
 
-message ListconfigsConfigsDeveloper {
-	bool set = 1;
+message ListconfigsConfigsAlias {
+	string value_str = 1;
 	string source = 2;
 }
 
-message ListconfigsConfigsClearplugins {
-	bool set = 1;
+message ListconfigsConfigsAllowdeprecatedapis {
+	bool value_bool = 1;
 	string source = 2;
 }
 
-message ListconfigsConfigsDisablempp {
-	bool set = 1;
+message ListconfigsConfigsAlwaysuseproxy {
+	bool value_bool = 1;
 	string source = 2;
-	optional string plugin = 3;
 }
 
-message ListconfigsConfigsMainnet {
-	bool set = 1;
-	string source = 2;
+message ListconfigsConfigsAnnounceaddr {
+	repeated string values_str = 1;
+	repeated string sources = 2;
 }
 
-message ListconfigsConfigsRegtest {
-	bool set = 1;
+message ListconfigsConfigsAnnounceaddrdiscovered {
+	// ListConfigs.configs.announce-addr-discovered.value_str
+	enum ListconfigsConfigsAnnounceaddrdiscoveredValueStr {
+		TRUE = 0;
+		FALSE = 1;
+		AUTO = 2;
+	}
+	ListconfigsConfigsAnnounceaddrdiscoveredValueStr value_str = 1;
 	string source = 2;
 }
 
-message ListconfigsConfigsSignet {
-	bool set = 1;
+message ListconfigsConfigsAnnounceaddrdiscoveredport {
+	uint32 value_int = 1;
 	string source = 2;
 }
 
-message ListconfigsConfigsTestnet {
-	bool set = 1;
+message ListconfigsConfigsAnnounceaddrdns {
+	bool value_bool = 1;
 	string source = 2;
 }
 
-message ListconfigsConfigsImportantplugin {
-	repeated string values_str = 1;
-	repeated string sources = 2;
+message ListconfigsConfigsAutoconnectseekerpeers {
+	uint32 value_int = 1;
+	string source = 2;
 }
 
-message ListconfigsConfigsPlugin {
-	repeated string values_str = 1;
-	repeated string sources = 2;
+message ListconfigsConfigsAutolisten {
+	bool value_bool = 1;
+	string source = 2;
 }
 
-message ListconfigsConfigsPlugindir {
+message ListconfigsConfigsBindaddr {
 	repeated string values_str = 1;
 	repeated string sources = 2;
 }
 
-message ListconfigsConfigsLightningdir {
-	string value_str = 1;
+message ListconfigsConfigsClearplugins {
+	bool set = 1;
 	string source = 2;
 }
 
-message ListconfigsConfigsNetwork {
-	string value_str = 1;
+message ListconfigsConfigsCltvdelta {
+	uint32 value_int = 1;
 	string source = 2;
 }
 
-message ListconfigsConfigsAllowdeprecatedapis {
-	bool value_bool = 1;
+message ListconfigsConfigsCltvfinal {
+	uint32 value_int = 1;
 	string source = 2;
 }
 
-message ListconfigsConfigsRpcfile {
-	string value_str = 1;
+message ListconfigsConfigsCommitfee {
+	uint64 value_int = 1;
 	string source = 2;
 }
 
-message ListconfigsConfigsDisableplugin {
-	repeated string values_str = 1;
-	repeated string sources = 2;
-}
-
-message ListconfigsConfigsAlwaysuseproxy {
-	bool value_bool = 1;
+message ListconfigsConfigsCommitfeerateoffset {
+	uint32 value_int = 1;
 	string source = 2;
 }
 
-message ListconfigsConfigsDaemon {
-	bool set = 1;
+message ListconfigsConfigsCommittime {
+	uint32 value_int = 1;
 	string source = 2;
 }
 
-message ListconfigsConfigsWallet {
+message ListconfigsConfigsConf {
+	// ListConfigs.configs.conf.source
+	enum ListconfigsConfigsConfSource {
+		CMDLINE = 0;
+	}
 	string value_str = 1;
-	string source = 2;
-}
-
-message ListconfigsConfigsLargechannels {
-	bool set = 1;
-	string source = 2;
+	ListconfigsConfigsConfSource source = 2;
 }
 
-message ListconfigsConfigsExperimentaldualfund {
-	bool set = 1;
-	string source = 2;
+message ListconfigsConfigsCurrencyrateaddsource {
+	repeated string values_str = 1;
+	repeated string sources = 2;
+	optional string plugin = 3;
 }
 
-message ListconfigsConfigsExperimentalsplicing {
-	bool set = 1 [deprecated = true];
-	string source = 2 [deprecated = true];
+message ListconfigsConfigsCurrencyratedisablesource {
+	repeated string values_str = 1;
+	repeated string sources = 2;
+	optional string plugin = 3;
 }
 
-message ListconfigsConfigsExperimentalshutdownwrongfunding {
+message ListconfigsConfigsDaemon {
 	bool set = 1;
 	string source = 2;
 }
 
-message ListconfigsConfigsExperimentalpeerstorage {
-	bool set = 1;
+message ListconfigsConfigsDatabaseupgrade {
+	bool value_bool = 1;
 	string source = 2;
 }
 
-message ListconfigsConfigsExperimentalanchors {
+message ListconfigsConfigsDeveloper {
 	bool set = 1;
 	string source = 2;
 }
 
-message ListconfigsConfigsDatabaseupgrade {
-	bool value_bool = 1;
+message ListconfigsConfigsDisabledns {
+	bool set = 1;
 	string source = 2;
 }
 
-message ListconfigsConfigsRgb {
-	bytes value_str = 1;
+message ListconfigsConfigsDisablempp {
+	bool set = 1;
 	string source = 2;
+	optional string plugin = 3;
 }
 
-message ListconfigsConfigsAlias {
-	string value_str = 1;
-	string source = 2;
+message ListconfigsConfigsDisableplugin {
+	repeated string values_str = 1;
+	repeated string sources = 2;
 }
 
-message ListconfigsConfigsPidfile {
-	string value_str = 1;
+message ListconfigsConfigsEncryptedhsm {
+	bool set = 1;
 	string source = 2;
 }
 
-message ListconfigsConfigsIgnorefeelimits {
-	bool value_bool = 1;
+message ListconfigsConfigsExperimentalanchors {
+	bool set = 1;
 	string source = 2;
 }
 
-message ListconfigsConfigsWatchtimeblocks {
-	uint32 value_int = 1;
+message ListconfigsConfigsExperimentaldualfund {
+	bool set = 1;
 	string source = 2;
 }
 
-message ListconfigsConfigsFundingconfirms {
-	uint32 value_int = 1;
+message ListconfigsConfigsExperimentalpeerstorage {
+	bool set = 1;
 	string source = 2;
 }
 
-message ListconfigsConfigsCltvdelta {
-	uint32 value_int = 1;
+message ListconfigsConfigsExperimentalshutdownwrongfunding {
+	bool set = 1;
 	string source = 2;
 }
 
-message ListconfigsConfigsCltvfinal {
-	uint32 value_int = 1;
-	string source = 2;
+message ListconfigsConfigsExperimentalsplicing {
+	bool set = 1 [deprecated = true];
+	string source = 2 [deprecated = true];
 }
 
-message ListconfigsConfigsCommittime {
+message ListconfigsConfigsFeebase {
 	uint32 value_int = 1;
 	string source = 2;
 }
 
-message ListconfigsConfigsFeebase {
+message ListconfigsConfigsFeepersatoshi {
 	uint32 value_int = 1;
 	string source = 2;
 }
 
-message ListconfigsConfigsRescan {
-	sint64 value_int = 1;
+message ListconfigsConfigsFetchinvoicenoconnect {
+	bool set = 1;
 	string source = 2;
+	optional string plugin = 3;
 }
 
-message ListconfigsConfigsFeepersatoshi {
-	uint32 value_int = 1;
+message ListconfigsConfigsForcefeerates {
+	string value_str = 1;
 	string source = 2;
 }
 
-message ListconfigsConfigsMaxconcurrenthtlcs {
+message ListconfigsConfigsFundingconfirms {
 	uint32 value_int = 1;
 	string source = 2;
 }
 
-message ListconfigsConfigsHtlcminimummsat {
-	Amount value_msat = 1;
-	string source = 2;
-}
-
 message ListconfigsConfigsHtlcmaximummsat {
 	Amount value_msat = 1;
 	string source = 2;
 }
 
-message ListconfigsConfigsMaxdusthtlcexposuremsat {
+message ListconfigsConfigsHtlcminimummsat {
 	Amount value_msat = 1;
 	string source = 2;
 }
 
-message ListconfigsConfigsMincapacitysat {
-	uint64 value_int = 1;
+message ListconfigsConfigsIgnorefeelimits {
+	bool value_bool = 1;
 	string source = 2;
-	optional bool dynamic = 3;
 }
 
-message ListconfigsConfigsAddr {
+message ListconfigsConfigsImportantplugin {
 	repeated string values_str = 1;
 	repeated string sources = 2;
 }
 
-message ListconfigsConfigsAnnounceaddr {
-	repeated string values_str = 1;
-	repeated string sources = 2;
+message ListconfigsConfigsLargechannels {
+	bool set = 1;
+	string source = 2;
 }
 
-message ListconfigsConfigsBindaddr {
+message ListconfigsConfigsLightningdir {
+	string value_str = 1;
+	string source = 2;
+}
+
+message ListconfigsConfigsLogfile {
 	repeated string values_str = 1;
 	repeated string sources = 2;
 }
 
-message ListconfigsConfigsOffline {
-	bool set = 1;
+message ListconfigsConfigsLoglevel {
+	string value_str = 1;
 	string source = 2;
 }
 
-message ListconfigsConfigsAutolisten {
-	bool value_bool = 1;
+message ListconfigsConfigsLogprefix {
+	string value_str = 1;
 	string source = 2;
 }
 
-message ListconfigsConfigsProxy {
-	string value_str = 1;
+message ListconfigsConfigsLogtimestamps {
+	bool value_bool = 1;
 	string source = 2;
 }
 
-message ListconfigsConfigsDisabledns {
+message ListconfigsConfigsMainnet {
 	bool set = 1;
 	string source = 2;
 }
 
-message ListconfigsConfigsAnnounceaddrdiscovered {
-	// ListConfigs.configs.announce-addr-discovered.value_str
-	enum ListconfigsConfigsAnnounceaddrdiscoveredValueStr {
-		TRUE = 0;
-		FALSE = 1;
-		AUTO = 2;
-	}
-	ListconfigsConfigsAnnounceaddrdiscoveredValueStr value_str = 1;
+message ListconfigsConfigsMaxconcurrenthtlcs {
+	uint32 value_int = 1;
 	string source = 2;
 }
 
-message ListconfigsConfigsAnnounceaddrdiscoveredport {
-	uint32 value_int = 1;
+message ListconfigsConfigsMaxdusthtlcexposuremsat {
+	Amount value_msat = 1;
 	string source = 2;
 }
 
-message ListconfigsConfigsEncryptedhsm {
-	bool set = 1;
+message ListconfigsConfigsMincapacitysat {
+	uint64 value_int = 1;
 	string source = 2;
+	optional bool dynamic = 3;
 }
 
-message ListconfigsConfigsRpcfilemode {
+message ListconfigsConfigsNetwork {
 	string value_str = 1;
 	string source = 2;
 }
 
-message ListconfigsConfigsLoglevel {
-	string value_str = 1;
+message ListconfigsConfigsOffline {
+	bool set = 1;
 	string source = 2;
 }
 
-message ListconfigsConfigsLogprefix {
+message ListconfigsConfigsPidfile {
 	string value_str = 1;
 	string source = 2;
 }
 
-message ListconfigsConfigsLogfile {
+message ListconfigsConfigsPlugin {
 	repeated string values_str = 1;
 	repeated string sources = 2;
 }
 
-message ListconfigsConfigsLogtimestamps {
-	bool value_bool = 1;
-	string source = 2;
+message ListconfigsConfigsPlugindir {
+	repeated string values_str = 1;
+	repeated string sources = 2;
 }
 
-message ListconfigsConfigsForcefeerates {
+message ListconfigsConfigsProxy {
 	string value_str = 1;
 	string source = 2;
 }
 
-message ListconfigsConfigsSubdaemon {
-	repeated string values_str = 1;
-	repeated string sources = 2;
-}
-
-message ListconfigsConfigsFetchinvoicenoconnect {
+message ListconfigsConfigsRegtest {
 	bool set = 1;
 	string source = 2;
-	optional string plugin = 3;
 }
 
-message ListconfigsConfigsTorservicepassword {
-	string value_str = 1;
+message ListconfigsConfigsRequireconfirmedinputs {
+	bool value_bool = 1;
 	string source = 2;
 }
 
-message ListconfigsConfigsAnnounceaddrdns {
-	bool value_bool = 1;
+message ListconfigsConfigsRescan {
+	sint64 value_int = 1;
 	string source = 2;
 }
 
-message ListconfigsConfigsRequireconfirmedinputs {
-	bool value_bool = 1;
+message ListconfigsConfigsRgb {
+	bytes value_str = 1;
 	string source = 2;
 }
 
-message ListconfigsConfigsCommitfee {
-	uint64 value_int = 1;
+message ListconfigsConfigsRpcfile {
+	string value_str = 1;
 	string source = 2;
 }
 
-message ListconfigsConfigsCommitfeerateoffset {
-	uint32 value_int = 1;
+message ListconfigsConfigsRpcfilemode {
+	string value_str = 1;
 	string source = 2;
 }
 
-message ListconfigsConfigsAutoconnectseekerpeers {
-	uint32 value_int = 1;
+message ListconfigsConfigsSignet {
+	bool set = 1;
 	string source = 2;
 }
 
-message ListconfigsConfigsCurrencyrateaddsource {
+message ListconfigsConfigsSubdaemon {
 	repeated string values_str = 1;
 	repeated string sources = 2;
-	optional string plugin = 3;
 }
 
-message ListconfigsConfigsCurrencyratedisablesource {
-	repeated string values_str = 1;
-	repeated string sources = 2;
-	optional string plugin = 3;
+message ListconfigsConfigsTestnet {
+	bool set = 1;
+	string source = 2;
+}
+
+message ListconfigsConfigsTorservicepassword {
+	string value_str = 1;
+	string source = 2;
+}
+
+message ListconfigsConfigsWallet {
+	string value_str = 1;
+	string source = 2;
+}
+
+message ListconfigsConfigsWatchtimeblocks {
+	uint32 value_int = 1;
+	string source = 2;
 }
 
 message StopRequest {
@@ -3993,11 +3993,11 @@ message AskrenelistlayersLayers {
 	repeated AskrenelistlayersLayersNodeBiases node_biases = 9;
 }
 
-message AskrenelistlayersLayersCreatedChannels {
-	bytes source = 1;
-	bytes destination = 2;
-	string short_channel_id = 3;
-	Amount capacity_msat = 4;
+message AskrenelistlayersLayersBiases {
+	string short_channel_id_dir = 1;
+	sint64 bias = 2;
+	optional string description = 3;
+	optional uint64 timestamp = 4;
 }
 
 message AskrenelistlayersLayersChannelUpdates {
@@ -4017,11 +4017,11 @@ message AskrenelistlayersLayersConstraints {
 	optional uint64 timestamp = 6;
 }
 
-message AskrenelistlayersLayersBiases {
-	string short_channel_id_dir = 1;
-	sint64 bias = 2;
-	optional string description = 3;
-	optional uint64 timestamp = 4;
+message AskrenelistlayersLayersCreatedChannels {
+	bytes source = 1;
+	bytes destination = 2;
+	string short_channel_id = 3;
+	Amount capacity_msat = 4;
 }
 
 message AskrenelistlayersLayersNodeBiases {
@@ -4053,11 +4053,11 @@ message AskrenecreatelayerLayers {
 	repeated AskrenecreatelayerLayersNodeBiases node_biases = 9;
 }
 
-message AskrenecreatelayerLayersCreatedChannels {
-	bytes source = 1;
-	bytes destination = 2;
-	string short_channel_id = 3;
-	Amount capacity_msat = 4;
+message AskrenecreatelayerLayersBiases {
+	string short_channel_id_dir = 1;
+	sint64 bias = 2;
+	optional string description = 3;
+	optional uint64 timestamp = 4;
 }
 
 message AskrenecreatelayerLayersChannelUpdates {
@@ -4075,11 +4075,11 @@ message AskrenecreatelayerLayersConstraints {
 	optional Amount minimum_msat = 4;
 }
 
-message AskrenecreatelayerLayersBiases {
-	string short_channel_id_dir = 1;
-	sint64 bias = 2;
-	optional string description = 3;
-	optional uint64 timestamp = 4;
+message AskrenecreatelayerLayersCreatedChannels {
+	bytes source = 1;
+	bytes destination = 2;
+	string short_channel_id = 3;
+	Amount capacity_msat = 4;
 }
 
 message AskrenecreatelayerLayersNodeBiases {
@@ -4671,11 +4671,6 @@ message StreamCoinMovementRequest {
 }
 
 message CoinMovementNotification {
-	// coin_movement.type
-	enum CoinMovementType {
-		CHANNEL_MVT = 0;
-		CHAIN_MVT = 1;
-	}
 	// coin_movement.primary_tag
 	enum CoinMovementPrimaryTag {
 		DEPOSIT = 0;
@@ -4702,6 +4697,11 @@ message CoinMovementNotification {
 		PENALTY_ADJ = 21;
 		JOURNAL_ENTRY = 22;
 	}
+	// coin_movement.type
+	enum CoinMovementType {
+		CHANNEL_MVT = 0;
+		CHAIN_MVT = 1;
+	}
 	uint32 version = 1;
 	string coin_type = 2;
 	bytes node_id = 3;
```

### contrib/msggen/msggen/model.py
```diff
@@ -246,7 +246,7 @@ def from_js(cls, js, path):
 
         def merge_dicts(dict1, dict2):
             merged_dict = {}
-            for key in set(dict1.keys()) | set(dict2.keys()):
+            for key in sorted(set(dict1.keys()) | set(dict2.keys())):
                 if key in dict1 and key in dict2:
                     if isinstance(dict1[key], dict) and isinstance(dict2[key], dict):
                         merged_dict[key] = merge_dicts(dict1[key], dict2[key])
@@ -285,7 +285,7 @@ def merge_dicts(dict1, dict2):
         # Identify required fields
         required = js.get("required", [])
         fields = []
-        for fname, ftype in properties.items():
+        for fname, ftype in sorted(properties.items(), key=lambda x: x[0]):
             field = None
             desc = ftype["description"] if "description" in ftype else ""
             fpath = f"{path}.{fname}"
```
