Based on my investigation, the strongest analog to the Discourse-Jira SSRF/path-manipulation bug (CVE-2023-44384) is in the CatFee TRON energy-purchase client, not in the on-chain dispatch path. I was not able to fully trace the exact call site in `tx.rs` that supplies `receiver_address`/`order_id` into `create_order`/`get_order_detail` due to running out of tool budget, so that link should be verified before treating this as fully confirmed. I flag that gap explicitly below.

### Title
Unsanitized interpolation of transaction-derived values into the CatFee API request path enables request/parameter injection using the relayer's live API credentials - (File: tesseract/messaging/tron/src/catfee.rs)

### Summary
`CatFeeClient::create_order` and `CatFeeClient::get_order_detail` build the CatFee HTTP request path with raw `format!` string interpolation of `receiver_address`/`order_id`, then sign that exact (already-injected) path with the operator's live `CF-ACCESS-KEY`/`CF-ACCESS-SIGN` HMAC credentials, and finally concatenate it onto the trusted `api_base` to form the request URL [1](#0-0) . This mirrors the Discourse-Jira bug class where a less-trusted actor manipulates the request path/parameters sent to a third-party API, letting them ride on stored, higher-privileged credentials to reach unintended endpoints or inject extra parameters.

### Finding Description
`create_order` builds the path as:
```
/v1/order?quantity={energy_amount}&receiver={receiver_address}&duration={period}h
```
with no validation that `receiver_address` is a well-formed TRON address (no character allow-list, no URL-encoding) [1](#0-0) . The HMAC signature is computed over this same string via `generate_signature(timestamp, method, request_path)` [2](#0-1) , so signature validity does not constrain the path's contents — whatever string ends up in `request_path` gets a valid signature and is sent with the operator's real API key. `get_order_detail` has the same pattern with `order_id` inserted unsanitized into `/v1/order/{order_id}` [3](#0-2) .

If `receiver_address` (or `order_id`) is derived from attacker-influenced transaction/message data processed by the TRON messaging relayer (the "bandwidth purchaser" role explicitly called out as in-scope), an attacker can inject additional `&param=value` query parameters, or characters that alter the path, into the signed request sent to `https://api.catfee.io`, using the tesseract operator's authenticated CatFee session — structurally the same primitive as the Jira bug ("a moderator user could manipulate the request path to the Jira API, allowing them to perform arbitrary GET requests using the Jira API credentials").

**Unverified link:** I could not confirm within this session's tool budget the exact call site in `tesseract/messaging/tron/src/tx.rs` that supplies `receiver_address`/`order_id` to these functions, so I cannot state with certainty that these values are attacker-controlled versus operator-configured. This must be checked before treating the finding as fully proven.

### Impact Explanation
If the interpolated fields are attacker-influenced, this allows arbitrary manipulation of a signed, credentialed HTTP request against the CatFee paid energy-purchase API. Depending on what CatFee's API accepts on unexpected parameters, consequences range from placing energy orders paid for by the operator's CatFee balance for an address of the attacker's choosing (fund drain via the CatFee balance) to leaking order data for arbitrary `order_id`s, or otherwise abusing the operator's live API credentials — a concrete funds-at-risk / unauthorized-action scenario, matching the CVSS Medium classification of the original report.

### Likelihood Explanation
Likelihood is currently **unconfirmed** pending verification that `receiver_address`/`order_id` originate from attacker-controlled transaction data (e.g., a destination address embedded in a relayed message rather than a value fixed by the tesseract operator's own signer/config). If confirmed attacker-controlled, likelihood is high, since it requires only a single relayed transaction/message with a crafted destination string and no special privilege.

### Recommendation
- Trace and confirm the callers of `create_order`/`get_order_detail` in `tesseract/messaging/tron/src/tx.rs` and `lib.rs` to determine whether `receiver_address`/`order_id` can be influenced by data from a relayed/dispatched transaction.
- Validate `receiver_address` as a well-formed TRON address (base58/hex, fixed length, allow-listed character set) before interpolation.
- Validate `order_id` format before interpolation.
- Prefer building the request with a proper URL/query-builder (percent-encoding parameter values) rather than manual `format!` string concatenation, and compute the HMAC signature over the final, validated path only.

### Proof of Concept
Not independently verified against a live call site; conceptually: submit a transaction/message such that the value routed into `receiver_address` contains `&extra=param` or path-altering characters, then observe the resulting outbound request to `https://api.catfee.io` (via logs at `catfee.rs:142` trace logging) carrying the injected content signed with the operator's real CatFee credentials [4](#0-3) .

### Citations

**File:** tesseract/messaging/tron/src/catfee.rs (L93-101)
```rust
	fn generate_signature(&self, timestamp: &str, method: &str, request_path: &str) -> String {
		let message = format!("{}{}{}", timestamp, method, request_path);

		let mut mac = HmacSha256::new_from_slice(self.config.api_secret.as_bytes())
			.expect("HMAC can take key of any size");
		mac.update(message.as_bytes());

		BASE64.encode(mac.finalize().into_bytes())
	}
```

**File:** tesseract/messaging/tron/src/catfee.rs (L123-141)
```rust
	pub async fn create_order(
		&self,
		energy_amount: u64,
		receiver_address: &str,
		period: u32,
	) -> anyhow::Result<CreateOrderResponse> {
		// Validate period
		if period != 1 && period != 24 {
			return Err(anyhow!("Invalid period: must be 1 or 24 hours"));
		}

		let request_path = format!(
			"/v1/order?quantity={}&receiver={}&duration={}h",
			energy_amount, receiver_address, period
		);
		let timestamp = Self::get_timestamp();
		let signature = self.generate_signature(&timestamp, "POST", &request_path);

		let url = format!("{}{}", self.config.api_base, request_path);
```

**File:** tesseract/messaging/tron/src/catfee.rs (L142-158)
```rust
		log::trace!(
			target: crate::LOG_TARGET, "Creating order: energy={}, receiver={}, period={}h",
			energy_amount,
			receiver_address,
			period
		);

		let response = self
			.client
			.post(&url)
			.header("Content-Type", "application/json")
			.header("CF-ACCESS-KEY", &self.config.api_key)
			.header("CF-ACCESS-SIGN", &signature)
			.header("CF-ACCESS-TIMESTAMP", &timestamp)
			.send()
			.await
			.context("Failed to send create order request")?;
```

**File:** tesseract/messaging/tron/src/catfee.rs (L191-208)
```rust
	pub async fn get_order_detail(&self, order_id: &str) -> anyhow::Result<OrderDetailResponse> {
		let request_path = format!("/v1/order/{}", order_id);
		let timestamp = Self::get_timestamp();
		let signature = self.generate_signature(&timestamp, "GET", &request_path);

		let url = format!("{}{}", self.config.api_base, request_path);
		log::trace!(target: crate::LOG_TARGET, "Querying order detail: {}", order_id);

		let response = self
			.client
			.get(&url)
			.header("Content-Type", "application/json")
			.header("CF-ACCESS-KEY", &self.config.api_key)
			.header("CF-ACCESS-SIGN", &signature)
			.header("CF-ACCESS-TIMESTAMP", &timestamp)
			.send()
			.await
			.context("Failed to send order detail request")?;
```
