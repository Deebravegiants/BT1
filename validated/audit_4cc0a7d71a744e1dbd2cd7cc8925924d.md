### Title
CatFee API secret logged in plaintext at info level on TRON relayer startup - (File: tesseract/messaging/tron/src/lib.rs)

### Summary
`TronClient::new` in the tesseract TRON messaging relayer logs the entire `CatFeeConfig` struct — which derives `Debug` and contains the plaintext `api_key` and `api_secret` fields used for HMAC-signing CatFee (energy/bandwidth purchasing) API requests — at `log::info!` level whenever CatFee credentials are configured.

### Finding Description
`CatFeeConfig` is defined with `#[derive(Debug, Clone)]` and stores `api_key` and `api_secret` as plain `String` fields with no redaction: [1](#0-0) 

When a relayer operator configures CatFee credentials to purchase TRON energy/bandwidth for transaction submission, `TronClient::new` builds this config and immediately logs it with the `{:#?}` (pretty Debug) formatter at `info` level: [2](#0-1) 

Because `api_secret` is a plain field with no custom `Debug` impl (no `SecretString`/redaction wrapper), the derived `Debug` output includes the raw secret value verbatim. This is the exact bug class described in the WildFly analog (CVE-2020-25640 / CWE-209 / CWE-532): a credential used to authenticate to an external service is written to application logs at a routine (non-error, always-emitted) log level rather than being suppressed or masked. This is reachable simply by any relayer operator running the `messaging-tron` node with `catfee_api_key`/`catfee_api_secret` set in `TronConfig`, which is the intended and documented configuration path for bandwidth purchasing (`CatFee integration enabled`), not an error/edge-case path — the log fires unconditionally on every relayer startup once configured.

For comparison, the codebase elsewhere shows an established pattern of masking secrets before logging/display (e.g., `maskSecret`/`maskToml` in the simplex filler config), which is not applied here: [3](#0-2) 

### Impact Explanation
Log files for the TRON relayer component are commonly aggregated, shipped to log-management/monitoring systems, or persisted with broader access than the process's own secrets store. Any actor with log access (log-shipping infra, ops tooling, cloud log buckets, or in worse setups, another tenant/service reading shared logs) obtains the plaintext CatFee `api_key`/`api_secret`. With that HMAC secret, an attacker can forge valid `CF-ACCESS-SIGN` signatures and impersonate the relayer operator against the CatFee API to place unauthorized energy-purchase orders, potentially draining the operator's CatFee account balance/funds used to pay for TRON bandwidth/energy — a concrete funds-loss impact on the bandwidth-purchasing component named as in-scope. This is not a network-level or malicious-admin scenario; it is a direct code defect that leaks a real, funds-authorizing credential into ordinary logs of a component that is part of the standard relayer transaction-submission pipeline for TRON.

### Likelihood Explanation
Likelihood is high for any relayer operator who enables CatFee (the documented, supported flow for TRON energy/bandwidth purchasing): the log line executes unconditionally at `info` level (not `debug`/`trace`, and not gated on an error condition), so it will appear in essentially every production log stream for `messaging-tron` whenever the feature is used. No attacker action against the chain or protocol is required to trigger the leak — only ordinary operational log collection/retention, matching the low-complexity, routine-operation nature of the original WildFly advisory.

### Recommendation
Do not log the full `CatFeeConfig` struct. Implement a custom `Debug`/`Display` for `CatFeeConfig` that redacts `api_key` and `api_secret` (e.g., masking to `***` or last 4 chars only), or log only non-sensitive fields (`api_base`, `timeout`) explicitly instead of `{:#?}` on the whole struct. Wrap `api_secret` (and ideally `api_key`) in a secret-wrapper type (e.g., `secrecy::SecretString`) whose `Debug` impl never reveals the inner value, so any future accidental logging elsewhere is also safe by default.

### Proof of Concept
1. Configure a `messaging-tron` relayer node with `catfee_api_key` and `catfee_api_secret` set (the documented CatFee integration path).
2. Start the relayer; `TronClient::new` executes: [4](#0-3) 
3. Inspect the relayer's stdout/log file — the `CatFee integration enabled: {config}` line contains the plaintext `api_secret` value because `CatFeeConfig` derives `Debug` with no field redaction: [1](#0-0) 
4. Anyone with read access to that log (log aggregator, monitoring stack, shared filesystem) can extract `api_secret` and forge `CF-ACCESS-SIGN` HMAC headers to call the CatFee API as the operator, per the documented signing scheme: [5](#0-4)

### Citations

**File:** tesseract/messaging/tron/src/catfee.rs (L44-54)
```rust
#[derive(Debug, Clone)]
pub struct CatFeeConfig {
	/// API key for authentication (required)
	pub api_key: String,
	/// API secret for HMAC signature generation (required)
	pub api_secret: String,
	/// Base URL for the CatFee API
	pub api_base: String,
	/// HTTP request timeout
	pub timeout: Duration,
}
```

**File:** tesseract/messaging/tron/src/catfee.rs (L89-101)
```rust
	/// Generate HMAC signature for API request
	///
	/// Signature format: Base64(HMAC-SHA256(secret, timestamp + method + requestPath))
	/// where requestPath includes query parameters
	fn generate_signature(&self, timestamp: &str, method: &str, request_path: &str) -> String {
		let message = format!("{}{}{}", timestamp, method, request_path);

		let mut mac = HmacSha256::new_from_slice(self.config.api_secret.as_bytes())
			.expect("HMAC can take key of any size");
		mac.update(message.as_bytes());

		BASE64.encode(mac.finalize().into_bytes())
	}
```

**File:** tesseract/messaging/tron/src/lib.rs (L247-261)
```rust
		// Initialize CatFee client if API credentials are provided
		let catfee = if let (Some(api_key), Some(api_secret)) =
			(&config.catfee_api_key, &config.catfee_api_secret)
		{
			let catfee_config = CatFeeConfig {
				api_key: api_key.clone(),
				api_secret: api_secret.clone(),
				timeout: std::time::Duration::from_secs(config.tron_api_timeout_secs),
				..Default::default()
			};
			log::info!(target: LOG_TARGET, "CatFee integration enabled: {:#?}", catfee_config);
			Some(CatFeeClient::new(catfee_config)?)
		} else {
			log::info!(target: LOG_TARGET, "CatFee integration disabled (API credentials not provided)");
			None
```

**File:** sdk/packages/simplex/src/services/server/setup-api.ts (L322-336)
```typescript
/** Display-only TOML with every secret masked; the round-trip gate runs on the real config. */
export function maskToml(config: FillerConfigFile, chainLabels?: string[]): string {
	const masked: FillerConfigFile = JSON.parse(JSON.stringify(config))
	const signer = masked.simplex.signer as Record<string, string> | undefined
	if (signer) {
		for (const field of ["key", "apiToken", "apiPrivateKey"]) {
			if (signer[field]) signer[field] = maskSecret(signer[field])
		}
	}
	if (masked.simplex.substratePrivateKey) {
		masked.simplex.substratePrivateKey = maskSecret(masked.simplex.substratePrivateKey)
	}
	if (masked.binance) {
		masked.binance.apiKey = maskSecret(masked.binance.apiKey)
		masked.binance.apiSecret = maskSecret(masked.binance.apiSecret)
```
