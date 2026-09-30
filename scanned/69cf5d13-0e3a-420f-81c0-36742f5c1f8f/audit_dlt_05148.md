# [?] Add LSPS5 DOS protections.

## Summary
Severity: Unknown
Chain: Bitcoin/Lightning
Component: lightningdevkit/rust-lightning
Published: 2025-08-07
Source: https://github.com/lightningdevkit/rust-lightning/commit/4370cffdb011f2bfadaa32a66e989c3c8f70feb0
Type: security-commit

## Details
Add LSPS5 DOS protections.

When handling an incoming LSPS5 request, the manager will check
if the counterparty is 'engaged' in some way before responding.
`Engaged` meaning = active channel | LSPS2 active operation | LSPS1 active operation.

Logic: `If not engaged then reject request;`

A single test is added only checking for the active channel condition,
because it's not super easy to get LSPS1-2 on the correct state to check this (yet).
Other tangential work is happening that will make this easier and more tests will come in the near future

## Patch
### lightning-liquidity/src/lsps1/service.rs
```diff
@@ -174,6 +174,20 @@ where
 		&self.config
 	}
 
+	/// Returns whether the peer currently has any active LSPS1 order flows.
+	///
+	/// An order is considered active only after we have validated the client's
+	/// `CreateOrder` request and replied with a `CreateOrder` response containing
+	/// an `order_id`.
+	/// Pending requests that are still awaiting our response are deliberately NOT counted.
+	pub(crate) fn has_active_requests(&self, counterparty_node_id: &PublicKey) -> bool {
+		let outer_state_lock = self.per_peer_state.read().unwrap();
+		outer_state_lock.get(counterparty_node_id).map_or(false, |inner| {
+			let peer_state = inner.lock().unwrap();
+			!peer_state.outbound_channels_by_order_id.is_empty()
+		})
+	}
+
 	fn handle_get_info_request(
 		&self, request_id: LSPSRequestId, counterparty_node_id: &PublicKey,
 	) -> Result<(), LightningError> {
```

### lightning-liquidity/src/lsps2/service.rs
```diff
@@ -566,6 +566,15 @@ where
 		&self.config
 	}
 
+	/// Returns whether the peer has any active LSPS2 requests.
+	pub(crate) fn has_active_requests(&self, counterparty_node_id: &PublicKey) -> bool {
+		let outer_state_lock = self.per_peer_state.read().unwrap();
+		outer_state_lock.get(counterparty_node_id).map_or(false, |inner| {
+			let peer_state = inner.lock().unwrap();
+			!peer_state.outbound_channels_by_intercept_scid.is_empty()
+		})
+	}
+
 	/// Used by LSP to inform a client requesting a JIT Channel the token they used is invalid.
 	///
 	/// Should be called in response to receiving a [`LSPS2ServiceEvent::GetInfo`] event.
```

### lightning-liquidity/src/lsps5/client.rs
```diff
@@ -185,6 +185,9 @@ where
 	/// Also ensure the URL is valid, has HTTPS protocol, its length does not exceed [`MAX_WEBHOOK_URL_LENGTH`]
 	/// and that the URL points to a public host.
 	///
+	/// Your request may fail if you recently opened a channel or started an LSPS1 / LSPS2 flow.
+	/// Please retry shortly.
+	///
 	/// [`MAX_WEBHOOK_URL_LENGTH`]: super::msgs::MAX_WEBHOOK_URL_LENGTH
 	/// [`MAX_APP_NAME_LENGTH`]: super::msgs::MAX_APP_NAME_LENGTH
 	/// [`WebhookRegistered`]: super::event::LSPS5ClientEvent::WebhookRegistered
```

### lightning-liquidity/src/lsps5/msgs.rs
```diff
@@ -53,6 +53,8 @@ pub const LSPS5_UNKNOWN_ERROR_CODE: i32 = 1000;
 pub const LSPS5_SERIALIZATION_ERROR_CODE: i32 = 1001;
 /// A notification was sent too frequently.
 pub const LSPS5_SLOW_DOWN_ERROR_CODE: i32 = 1002;
+/// A request was rejected because the client has no prior activity with the LSP (no open channel and no active LSPS1 or LSPS2 flow). The client should first open a channel
+pub const LSPS5_NO_PRIOR_ACTIVITY_ERROR_CODE: i32 = 1003;
 
 pub(crate) const LSPS5_SET_WEBHOOK_METHOD_NAME: &str = "lsps5.set_webhook";
 pub(crate) const LSPS5_LIST_WEBHOOKS_METHOD_NAME: &str = "lsps5.list_webhooks";
@@ -113,6 +115,10 @@ pub enum LSPS5ProtocolError {
 	///
 	/// [`NOTIFICATION_COOLDOWN_TIME`]: super::service::NOTIFICATION_COOLDOWN_TIME
 	SlowDownError,
+
+	/// Request rejected because the client has no prior activity with the LSP (no open channel and no active LSPS1 or LSPS2 flow). The client should first open a channel
+	/// or initiate an LSPS1/LSPS2 interaction before retrying.
+	NoPriorActivityError,
 }
 
 impl LSPS5ProtocolError {
@@ -129,6 +135,7 @@ impl LSPS5ProtocolError {
 			LSPS5ProtocolError::UnknownError => LSPS5_UNKNOWN_ERROR_CODE,
 			LSPS5ProtocolError::SerializationError => LSPS5_SERIALIZATION_ERROR_CODE,
 			LSPS5ProtocolError::SlowDownError => LSPS5_SLOW_DOWN_ERROR_CODE,
+			LSPS5ProtocolError::NoPriorActivityError => LSPS5_NO_PRIOR_ACTIVITY_ERROR_CODE,
 		}
 	}
 	/// The error message for the LSPS5 protocol error.
@@ -145,6 +152,9 @@ impl LSPS5ProtocolError {
 				"Error serializing LSPS5 webhook notification"
 			},
 			LSPS5ProtocolError::SlowDownError => "Notification sent too frequently",
+			LSPS5ProtocolError::NoPriorActivityError => {
+				"Request rejected due to no prior activity with the LSP"
+			},
 		}
 	}
 }
@@ -249,6 +259,9 @@ impl From<LSPSResponseError> for LSPS5ProtocolError {
 			LSPS5_UNSUPPORTED_PROTOCOL_ERROR_CODE => LSPS5ProtocolError::UnsupportedProtocol,
 			LSPS5_TOO_MANY_WEBHOOKS_ERROR_CODE => LSPS5ProtocolError::TooManyWebhooks,
 			LSPS5_APP_NAME_NOT_FOUND_ERROR_CODE => LSPS5ProtocolError::AppNameNotFound,
+			LSPS5_SERIALIZATION_ERROR_CODE => LSPS5ProtocolError::SerializationError,
+			LSPS5_SLOW_DOWN_ERROR_CODE => LSPS5ProtocolError::SlowDownError,
+			LSPS5_NO_PRIOR_ACTIVITY_ERROR_CODE => LSPS5ProtocolError::NoPriorActivityError,
 			_ => LSPS5ProtocolError::UnknownError,
 		}
 	}
@@ -640,6 +653,12 @@ pub enum LSPS5Request {
 	RemoveWebhook(RemoveWebhookRequest),
 }
 
+impl LSPS5Request {
+	pub(crate) fn is_state_allocating(&self) -> bool {
+		matches!(self, LSPS5Request::SetWebhook(_))
+	}
+}
+
 /// An LSPS5 protocol response.
 #[derive(Clone, Debug, PartialEq, Eq)]
 pub enum LSPS5Response {
```

### lightning-liquidity/src/lsps5/service.rs
```diff
@@ -149,6 +149,34 @@ where
 		}
 	}
 
+	/// Enforces the prior-activity requirement for state-allocating LSPS5 requests (e.g.
+	/// `lsps5.set_webhook`), rejecting and replying with `NoPriorActivityError` if not met.
+	pub(crate) fn enforce_prior_activity_or_reject(
+		&self, client_id: &PublicKey, lsps2_has_active_requests: bool, lsps1_has_activity: bool,
+		request_id: LSPSRequestId,
+	) -> Result<(), LightningError> {
+		let can_accept = self.client_has_open_channel(client_id)
+			|| lsps2_has_active_requests
+			|| lsps1_has_activity;
+
+		let mut message_queue_notifier = self.pending_messages.notifier();
+		if !can_accept {
+			let error = LSPS5ProtocolError::NoPriorActivityError;
+			let msg = LSPS5Message::Response(
+				request_id,
+				LSPS5Response::SetWebhookError(error.clone().into()),
+			)
+			.into();
+			message_queue_notifier.enqueue(&client_id, msg);
+			return Err(LightningError {
+				err: error.message().into(),
+				action: ErrorAction::IgnoreAndLog(Level::Info),
+			});
+		} else {
+			Ok(())
+		}
+	}
+
 	fn check_prune_stale_webhooks<'a>(
 		&self, outer_state_lock: &mut RwLockWriteGuard<'a, HashMap<PublicKey, PeerState>>,
 	) {
```

### lightning-liquidity/src/manager.rs
```diff
@@ -568,6 +568,29 @@ where
 			LSPSMessage::LSPS5(msg @ LSPS5Message::Request(..)) => {
 				match &self.lsps5_service_handler {
 					Some(lsps5_service_handler) => {
+						if let LSPS5Message::Request(ref req_id, ref req) = msg {
+							if req.is_state_allocating() {
+								let lsps2_has_active_requests = self
+									.lsps2_service_handler
+									.as_ref()
+									.map_or(false, |h| h.has_active_requests(sender_node_id));
+								#[cfg(lsps1_service)]
+								let lsps1_has_active_requests = self
+									.lsps1_service_handler
+									.as_ref()
+									.map_or(false, |h| h.has_active_requests(sender_node_id));
+								#[cfg(not(lsps1_service))]
+								let lsps1_has_active_requests = false;
+
+								lsps5_service_handler.enforce_prior_activity_or_reject(
+									sender_node_id,
+									lsps2_has_active_requests,
+									lsps1_has_active_requests,
+									req_id.clone(),
+								)?
+							}
+						}
+
 						lsps5_service_handler.handle_message(msg, sender_node_id)?;
 					},
 					None => {
```

### lightning-liquidity/tests/lsps5_integration_tests.rs
```diff
@@ -2,16 +2,24 @@
 
 mod common;
 
-use common::{create_service_and_client_nodes, get_lsps_message, LSPSNodes};
+use common::{create_service_and_client_nodes, get_lsps_message, LSPSNodes, LiquidityNode};
 
+use lightning::check_closed_event;
+use lightning::events::ClosureReason;
+use lightning::ln::channelmanager::InterceptId;
 use lightning::ln::functional_test_utils::{
-	create_chanmon_cfgs, create_network, create_node_cfgs, create_node_chanmgrs, Node,
+	close_channel, create_chan_between_nodes, create_chanmon_cfgs, create_network,
+	create_node_cfgs, create_node_chanmgrs, Node,
 };
 use lightning::ln::msgs::Init;
 use lightning::ln::peer_handler::CustomMessageHandler;
 use lightning::util::hash_tables::{HashMap, HashSet};
 use lightning_liquidity::events::LiquidityEvent;
 use lightning_liquidity::lsps0::ser::LSPSDateTime;
+use lightning_liquidity::lsps2::client::LSPS2ClientConfig;
+use lightning_liquidity::lsps2::event::{LSPS2ClientEvent, LSPS2ServiceEvent};
+use lightning_liquidity::lsps2::msgs::LSPS2RawOpeningFeeParams;
+use lightning_liquidity::lsps2::service::LSPS2ServiceConfig;
 use lightning_liquidity::lsps5::client::LSPS5ClientConfig;
 use lightning_liquidity::lsps5::event::{LSPS5ClientEvent, LSPS5ServiceEvent};
 use lightning_liquidity::lsps5::msgs::{
@@ -27,6 +35,10 @@ use lightning_liquidity::lsps5::service::{
 use lightning_liquidity::lsps5::validator::{LSPS5Validator, MAX_RECENT_SIGNATURES};
 use lightning_liquidity::utils::time::{DefaultTimeProvider, TimeProvider};
 use lightning_liquidity::{LiquidityClientConfig, LiquidityServiceConfig};
+
+use lightning_types::payment::PaymentHash;
+
+use std::str::FromStr;
 use std::sync::{Arc, RwLock};
 use std::time::Duration;
 
@@ -62,6 +74,180 @@ pub(crate) fn lsps5_test_setup<'a, 'b, 'c>(
 	(lsps_nodes, validator)
 }
 
+fn assert_lsps5_reject(
+	service_node: &LiquidityNode<'_, '_, '_>, client_node: &LiquidityNode<'_, '_, '_>,
+) {
+	let client_handler = client_node.liquidity_manager.lsps5_client_handler().unwrap();
+	let service_node_id = service_node.inner.node.get_our_node_id();
+	let client_node_id = client_node.inner.node.get_our_node_id();
+
+	let _ = client_handler
+		.set_webhook(service_node_id, "App".to_string(), "https://example.org/webhook".to_string())
+		.expect("Request should send");
+	let request = get_lsps_message!(client_node, service_node_id);
+
+	let service_result =
+		service_node.liquidity_manager.handle_custom_message(request, client_node_id);
+	assert!(service_result.is_err(), "Service should reject request without prior interaction");
+
+	let req = get_lsps_message!(service_node, client_node_id);
+	client_node.liquidity_manager.handle_custom_message(req, service_node_id).unwrap();
+	let event = client_node.liquidity_manager.next_event().unwrap();
+	match event {
+		LiquidityEvent::LSPS5Client(LSPS5ClientEvent::WebhookRegistrationFailed {
+			error, ..
+		}) => {
+			let error_to_check = LSPS5ProtocolError::NoPriorActivityError;
+			assert_eq!(error, error_to_check.into());
+		},
+		_ => panic!("Expected WebhookRegistrationFailed event, got {:?}", event),
+	}
+}
+
+fn assert_lsps5_accept(
+	service_node: &LiquidityNode<'_, '_, '_>, client_node: &LiquidityNode<'_, '_, '_>,
+) {
+	let client_handler = client_node.liquidity_manager.lsps5_client_handler().unwrap();
+	let service_node_id = service_node.inner.node.get_our_node_id();
+	let client_node_id = client_node.inner.node.get_our_node_id();
+
+	let _ = client_handler
+		.set_webhook(service_node_id, "App".to_string(), "https://example.org/webhook".to_string())
+		.expect("Request should send");
+	let request = get_lsps_message!(client_node, service_node_id);
+
+	let result = service_node.liquidity_manager.handle_custom_message(request, client_node_id);
+	assert!(result.is_ok(), "Service should accept request after prior interaction");
+	let _ = service_node.liquidity_manager.next_event().unwrap();
+	let response = get_lsps_message!(service_node, client_node_id);
+	client_node
+		.liquidity_manager
+		.handle_custom_message(response, service_node_id)
+		.expect("Client should handle response");
+	let event = client_node.liquidity_manager.next_event().unwrap();
+	match event {
+		LiquidityEvent::LSPS5Client(LSPS5ClientEvent::WebhookRegistered { .. }) => {},
+		_ => panic!("Expected WebhookRegistered event, got {:?}", event),
+	}
+}
+
+fn establish_lsps2_prior_interaction(lsps_nodes: &LSPSNodes) {
+	let service_node = &lsps_nodes.service_node;
+	let client_node = &lsps_nodes.client_node;
+
+	let service_node_id = service_node.inner.node.get_our_node_id();
+	let client_node_id = client_node.inner.node.get_our_node_id();
+
+	let lsps2_client = client_node.liquidity_manager.lsps2_client_handler().unwrap();
+	let lsps2_service = service_node.liquidity_manager.lsps2_service_handler().unwrap();
+
+	let get_info_request_id = lsps2_client.request_opening_params(service_node_id, None);
+	let get_info_req = get_lsps_message!(client_node, service_node_id);
+	service_node.liquidity_manager.handle_custom_message(get_info_req, client_node_id).unwrap();
+
+	let get_info_event = service_node.liquidity_manager.next_event().unwrap();
+	let opening_fee_params = match get_info_event {
+		LiquidityEvent::LSPS2Service(LSPS2ServiceEvent::GetInfo {
+			request_id,
+			counterparty_node_id,
+			..
+		}) => {
+			assert_eq!(request_id, get_info_request_id);
+			assert_eq!(counterparty_node_id, client_node_id);
+			let raw_opening_params = LSPS2RawOpeningFeeParams {
+				min_fee_msat: 1000,
+				proportional: 0,
+				valid_until: LSPSDateTime::from_str("2035-05-20T08:30:45Z").unwrap(),
+				min_lifetime: 144,
+				max_client_to_self_delay: 144,
+				min_payment_size_msat: 1,
+				max_payment_size_msat: 1_000_000_000,
+			};
+			lsps2_service
+				.opening_fee_params_generated(
+					&client_node_id,
+					request_id.clone(),
+					vec![raw_opening_params],
+				)
+				.unwrap();
+			let response = get_lsps_message!(service_node, client_node_id);
+			client_node.liquidity_manager.handle_custom_message(response, service_node_id).unwrap();
+			match client_node.liquidity_manager.next_event().unwrap() {
+				LiquidityEvent::LSPS2Client(LSPS2ClientEvent::OpeningParametersReady {
+					opening_fee_params_menu,
+					..
+				}) => opening_fee_params_menu.first().unwrap().clone(),
+				_ => panic!("Unexpected event"),
+			}
+		},
+		_ => panic!("Unexpected event"),
+	};
+
+	let payment_size_msat = Some(1_000_000);
+	let buy_request_id = lsps2_client
+		.select_opening_params(service_node_id, payment_size_msat, opening_fee_params.clone())
+		.unwrap();
+	let buy_req = get_lsps_message!(client_node, service_node_id);
+	service_node.liquidity_manager.handle_custom_message(buy_req, client_node_id).unwrap();
+	let _ = service_node.liquidity_manager.next_event().unwrap();
+
+	let intercept_scid = service_node.inner.node.get_intercept_scid();
+	let user_channel_id = 7;
+	let cltv_expiry_delta = 144;
+	lsps2_service
+		.invoice_parameters_generated(
+			&client_node_id,
+			buy_request_id.clone(),
+			intercept_scid,
+			cltv_expiry_delta,
+			true,
+			user_channel_id,
+		)
+		.unwrap();
+	let buy_resp = get_lsps_message!(service_node, client_node_id);
+	client_node.liquidity_manager.handle_custom_message(buy_resp, service_node_id).unwrap();
+	let _ = client_node.liquidity_manager.next_event().unwrap();
+
+	let intercept_id = InterceptId([0; 32]);
+	let payment_hash = PaymentHash([1; 32]);
+	lsps2_service.htlc_intercepted(intercept_scid, intercept_id, 1_000_000, payment_hash).unwrap();
+
+	let _ = service_node.liquidity_manager.next_event().unwrap();
+}
+
+pub(crate) fn lsps5_lsps2_test_setup<'a, 'b, 'c>(
+	nodes: Vec<Node<'a, 'b, 'c>>, time_provider: Arc<dyn TimeProvider + Send + Sync>,
+) -> (LSPSNodes<'a, 'b, 'c>, LSPS5Validator) {
+	let lsps5_service_config = LSPS5ServiceConfig::default();
+	let lsps2_service_config = LSPS2ServiceConfig { promise_secret: [42; 32] };
+	let service_config = LiquidityServiceConfig {
+		#[cfg(lsps1_service)]
+		lsps1_service_config: None,
+		lsps2_service_config: Some(lsps2_service_config),
+		lsps5_service_config: Some(lsps5_service_config),
+		advertise_service: true,
+	};
+
+	let lsps5_client_config = LSPS5ClientConfig::default();
+	let lsps2_client_config = LSPS2ClientConfig::default();
+	let client_config = LiquidityClientConfig {
+		lsps1_client_config: None,
+		lsps2_client_config: Some(lsps2_client_config),
+		lsps5_client_config: Some(lsps5_client_config),
+	};
+
+	let lsps_nodes = create_service_and_client_nodes(
+		nodes,
+		service_config,
+		client_config,
+		Arc::clone(&time_provider),
+	);
+
+	let validator = LSPS5Validator::new();
+
+	(lsps_nodes, validator)
+}
+
 struct MockTimeProvider {
 	current_time: RwLock<Duration>,
 }
@@ -102,7 +288,8 @@ fn webhook_registration_flow() {
 	let node_chanmgrs = create_node_chanmgrs(2, &node_cfgs, &[None, None]);
 	let nodes = create_network(2, &node_cfgs, &node_chanmgrs);
 	let (lsps_nodes, _) = lsps5_test_setup(nodes, Arc::new(DefaultTimeProvider));
-	let LSPSNodes { service_node, client_node } = lsps_nodes;
+	let LSPSNodes { service_node, client_node, .. } = lsps_nodes;
+	create_chan_between_nodes(&service_node.inner, &client_node.inner);
 	let service_node_id = service_node.inner.node.get_our_node_id();
 	let client_node_id = client_node.inner.node.get_our_node_id();
 	let client_handler = client_node.liquidity_manager.lsps5_client_handler().unwrap();
@@ -293,6 +480,7 @@ fn webhook_error_handling_test() {
 	let nodes = create_network(2, &node_cfgs, &node_chanmgrs);
 	let (lsps_nodes, _) = lsps5_test_setup(nodes, Arc::new(DefaultTimeProvider));
 	let LSPSNodes { service_node, client_node } = lsps_nodes;
+	create_chan_between_nodes(&service_node.inner, &client_node.inner);
 	let service_node_id = service_node.inner.node.get_our_node_id();
 	let client_node_id = client_node.inner.node.get_our_node_id();
 
@@ -419,6 +607,7 @@ fn webhook_notification_delivery_test() {
 	let nodes = create_network(2, &node_cfgs, &node_chanmgrs);
 	let (lsps_nodes, validator) = lsps5_test_setup(nodes, time_provider);
 	let LSPSNodes { service_node, client_node } = lsps_nodes;
+	create_chan_between_nodes(&service_node.inner, &client_node.inner);
 	let service_node_id = service_node.inner.node.get_our_node_id();
 	let client_node_id = client_node.inner.node.get_our_node_id();
 
@@ -529,6 +718,7 @@ fn multiple_webhooks_notification_test() {
 	let nodes = create_network(2, &node_cfgs, &node_chanmgrs);
 	let (lsps_nodes, _) = lsps5_test_setup(nodes, Arc::new(DefaultTimeProvider));
 	let LSPSNodes { service_node, client_node } = lsps_nodes;
+	create_chan_between_nodes(&service_node.inner, &client_node.inner);
 	let service_node_id = service_node.inner.node.get_our_node_id();
 	let client_node_id = client_node.inner.node.get_our_node_id();
 
@@ -629,6 +819,7 @@ fn idempotency_set_webhook_test() {
 	let nodes = create_network(2, &node_cfgs, &node_chanmgrs);
 	let (lsps_nodes, _) = lsps5_test_setup(nodes, Arc::new(DefaultTimeProvider));
 	let LSPSNodes { service_node, client_node } = lsps_nodes;
+	create_chan_between_nodes(&service_node.inner, &client_node.inner);
 	let service_node_id = service_node.inner.node.get_our_node_id();
 	let client_node_id = client_node.inner.node.get_our_node_id();
 
@@ -731,6 +922,7 @@ fn replay_prevention_test() {
 	let nodes = create_network(2, &node_cfgs, &node_chanmgrs);
 	let (lsps_nodes, validator) = lsps5_test_setup(nodes, time_provider);
 	let LSPSNodes { service_node, client_node } = lsps_nodes;
+	create_chan_between_nodes(&service_node.inner, &client_node.inner);
 	let service_node_id = service_node.inner.node.get_our_node_id();
 	let client_node_id = client_node.inner.node.get_our_node_id();
 
@@ -818,7 +1010,8 @@ fn stale_webhooks() {
 	let node_cfgs = create_node_cfgs(2, &chanmon_cfgs);
 	let node_chanmgrs = create_node_chanmgrs(2, &node_cfgs, &[None, None]);
 	let nodes = create_network(2, &node_cfgs, &node_chanmgrs);
-	let (lsps_nodes, _) = lsps5_test_setup(nodes, time_provider);
+	let (lsps_nodes, _) = lsps5_lsps2_test_setup(nodes, time_provider);
+	establish_lsps2_prior_interaction(&lsps_nodes);
 	let LSPSNodes { service_node, client_node } = lsps_nodes;
 	let service_node_id = service_node.inner.node.get_our_node_id();
 	let client_node_id = client_node.inner.node.get_our_node_id();
@@ -896,6 +1089,7 @@ fn test_all_notifications() {
 	let nodes = create_network(2, &node_cfgs, &node_chanmgrs);
 	let (lsps_nodes, validator) = lsps5_test_setup(nodes, time_provider);
 	let LSPSNodes { service_node, client_node } = lsps_nodes;
+	create_chan_between_nodes(&service_node.inner, &client_node.inner);
 	let service_node_id = service_node.inner.node.get_our_node_id();
 	let client_node_id = client_node.inner.node.get_our_node_id();
 
@@ -962,6 +1156,7 @@ fn test_tampered_notification() {
 	let nodes = create_network(2, &node_cfgs, &node_chanmgrs);
 	let (lsps_nodes, validator) = lsps5_test_setup(nodes, Arc::new(DefaultTimeProvider));
 	let LSPSNodes { service_node, client_node } = lsps_nodes;
+	create_chan_between_nodes(&service_node.inner, &client_node.inner);
 	let service_node_id = service_node.inner.node.get_our_node_id();
 	let client_node_id = client_node.inner.node.get_our_node_id();
 
@@ -1015,6 +1210,7 @@ fn test_bad_signature_notification() {
 	let nodes = create_network(2, &node_cfgs, &node_chanmgrs);
 	let (lsps_nodes, validator) = lsps5_test_setup(nodes, Arc::new(DefaultTimeProvider));
 	let LSPSNodes { service_node, client_node } = lsps_nodes;
+	create_chan_between_nodes(&service_node.inner, &client_node.inner);
 	let service_node_id = service_node.inner.node.get_our_node_id();
 	let client_node_id = client_node.inner.node.get_our_node_id();
 
@@ -1063,6 +1259,7 @@ fn test_notify_without_webhooks_does_nothing() {
 	let nodes = create_network(2, &node_cfgs, &node_chanmgrs);
 	let (lsps_nodes, _) = lsps5_test_setup(nodes, Arc::new(DefaultTimeProvider));
 	let LSPSNodes { service_node, client_node } = lsps_nodes;
+	create_chan_between_nodes(&service_node.inner, &client_node.inner);
 	let client_node_id = client_node.inner.node.get_our_node_id();
 
 	let service_handler = service_node.liquidity_manager.lsps5_service_handler().unwrap();
@@ -1085,6 +1282,7 @@ fn test_notifications_and_peer_connected_resets_cooldown() {
 	let nodes = create_network(2, &node_cfgs, &node_chanmgrs);
 	let (lsps_nodes, _) = lsps5_test_setup(nodes, time_provider);
 	let LSPSNodes { service_node, client_node } = lsps_nodes;
+	create_chan_between_nodes(&service_node.inner, &client_node.inner);
 	let service_node_id = service_node.inner.node.get_our_node_id();
 	let client_node_id = client_node.inner.node.get_our_node_id();
 
@@ -1183,6 +1381,7 @@ fn webhook_update_affects_future_notifications() {
 	let nodes = create_network(2, &node_cfgs, &node_chanmgrs);
 	let (lsps_nodes, _) = lsps5_test_setup(nodes, time_provider);
 	let LSPSNodes { service_node, client_node } = lsps_nodes;
+	create_chan_between_nodes(&service_node.inner, &client_node.inner);
 	let service_node_id = service_node.inner.node.get_our_node_id();
 	let client_node_id = client_node.inner.node.get_our_node_id();
 	let client_handler = client_node.liquidity_manager.lsps5_client_handler().unwrap();
@@ -1234,3 +1433,49 @@ fn webhook_update_affects_future_notifications() {
 		_ => panic!("Expected SendWebhookNotification after update"),
 	}
 }
+
+#[test]
+fn dos_protection() {
+	let chanmon_cfgs = create_chanmon_cfgs(2);
+	let node_cfgs = create_node_cfgs(2, &chanmon_cfgs);
+	let node_chanmgrs = create_node_chanmgrs(2, &node_cfgs, &[None, None]);
+	let nodes = create_network(2, &node_cfgs, &node_chanmgrs);
+	let (lsps_nodes, _) = lsps5_test_setup(nodes, Arc::new(DefaultTimeProvider));
+	let LSPSNodes { service_node, client_node } = lsps_nodes;
+	let client_node_id = client_node.inner.node.get_our_node_id();
+	let service_node_id = service_node.inner.node.get_our_node_id();
+
+	// no channel is open so far -> should reject
+	assert_lsps5_reject(&service_node, &client_node);
+
+	let (_, _, _, channel_id, funding_tx) =
+		create_chan_between_nodes(&service_node.inner, &client_node.inner);
+
+	// now that a channel is open, should accept
+	assert_lsps5_accept(&service_node, &client_node);
+
+	close_channel(&service_node.inner, &client_node.inner, &channel_id, funding_tx, true);
+	let node_a_reason = ClosureReason::CounterpartyInitiatedCooperativeClosure;
+	check_closed_event!(service_node.inner, 1, node_a_reason, [client_node_id], 100000);
+	let node_b_reason = ClosureReason::LocallyInitiatedCooperativeClosure;
+	check_closed_event!(client_node.inner, 1, node_b_reason, [service_node_id], 100000);
+
+	// channel is now closed again -> should reject
+	assert_lsps5_reject(&service_node, &client_node);
+}
+
+#[test]
+fn lsps2_state_allows_lsps5_request() {
+	let chanmon_cfgs = create_chanmon_cfgs(2);
+	let node_cfgs = create_node_cfgs(2, &chanmon_cfgs);
+	let node_chanmgrs = create_node_chanmgrs(2, &node_cfgs, &[None, None]);
+	let nodes = create_network(2, &node_cfgs, &node_chanmgrs);
+
+	let (lsps_nodes, _) = lsps5_lsps2_test_setup(nodes, Arc::new(DefaultTimeProvider));
+
+	assert_lsps5_reject(&lsps_nodes.service_node, &lsps_nodes.client_node);
+
+	establish_lsps2_prior_interaction(&lsps_nodes);
+
+	assert_lsps5_accept(&lsps_nodes.service_node, &lsps_nodes.client_node);
+}
```
