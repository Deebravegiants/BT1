### Title
Webhook Shop-Domain Spoofing via HMAC Scope Gap Enables Cross-Tenant Event Confusion - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC over the raw request body, then hands the handler a `shop` value that is read from an HTTP header that is **not** part of the signed payload. Because the `shop` identity field is decoupled from the HMAC binding, a previously captured valid `(body, hmac)` pair can be replayed with an arbitrary `shop-domain` header and will still pass validation, letting an attacker make the app process a legitimate Shopify-signed webhook body under a victim shop's identity.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

while `shop` is read independently from a header that is never validated against the HMAC: [2](#0-1) 

`HmacValidator.validate` computes the HMAC exclusively over `verifiable_query.to_signable_string` (i.e. the raw body) and compares it to the `hmac-sha256`/`x-shopify-hmac-sha256` header: [3](#0-2) 

`Registry.process` trusts this validation and then forwards `request.shop` — the unauthenticated header value — directly to the app's handler as the tenant identity for the event: [4](#0-3) 

The identity binding that should hold is: `shop header == shop covered by HMAC`. Instead, the gem enforces only `hmac(body) == received_hmac`, while `shop` is an out-of-band, unauthenticated header. Any request whose `(raw_body, hmac-sha256 header)` pair was ever legitimately produced by Shopify (e.g., a webhook the attacker's own store received, since anyone can install the app and generate real webhook traffic for their own shop) can be replayed to the app's public webhook endpoint with the `shop-domain`/`x-shopify-shop-domain` header rewritten to a victim's `myshopify.com` domain, and it will pass `Utils::HmacValidator.validate` unchanged because that header is outside the signed scope.

### Impact Explanation
This breaks the tenant-isolation guarantee the HMAC check is meant to provide: `WebhookMetadata#shop` (derived from `request.shop`) is the only tenant identifier passed to the host application's webhook handler, and it is unauthenticated. Host applications rely on this `shop` value to route data (e.g., look up which merchant's session/token to use, which merchant's records to update/delete). An attacker who can generate or intercept any one valid `(body, hmac)` pair (trivial — install the app themselves and trigger any webhook) can impersonate a different tenant's webhook event, causing cross-tenant data corruption/leakage in the host app depending on how it consumes `WebhookMetadata#shop`. This matches the Critical "cross-tenant access" impact category, since the gem itself is the component asserting the (broken) identity binding that downstream apps rely on.

### Likelihood Explanation
Webhook endpoints are public HTTP endpoints by design, so no privileged access is required. The only prerequisite is possession of one valid `(raw_body, hmac)` pair for any topic, which any user of the app (including the attacker, on their own store) can freely obtain through normal use, since Shopify will happily sign webhooks for any shop that installs the app. No secrets, tokens, or elevated access are needed to craft the malicious request — only forging the `shop-domain` header on replay.

### Recommendation
Include the shop domain (and ideally topic/webhook id) as part of the HMAC-signable material, or otherwise cryptographically bind `shop` to the validated payload, before it is included in `WebhookMetadata`. At minimum, `Registry.process` should reject requests where the shop cannot be independently corroborated (e.g., against a known/registered shop list) rather than trusting the raw header outright.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker.myshopify.com` and receives (or triggers) a legitimate webhook, capturing the raw body `B` and its `x-shopify-hmac-sha256: H` header — both computed by Shopify using the app's real secret.
2. Attacker sends a new POST request directly to the same app webhook endpoint with:
   - `raw_body = B` (unchanged)
   - `x-shopify-hmac-sha256: H` (unchanged)
   - `x-shopify-shop-domain: victim-shop.myshopify.com` (attacker-controlled)
   - `x-shopify-topic`, `x-shopify-webhook-id` unchanged or attacker-chosen
3. `ShopifyAPI::Webhooks::Request.new` accepts the headers, `Utils::HmacValidator.validate` succeeds because it only checks `hmac(B) == H`, which is unaffected by the spoofed `shop-domain` header.
4. `Registry.process` calls `handler.handle(data: WebhookMetadata.new(topic:, shop: "victim-shop.myshopify.com", body: parsed(B), ...))`, causing the host application to process the event as belonging to `victim-shop.myshopify.com` instead of the attacker's own shop.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-23)
```ruby
      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L35-38)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end
```

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

**File:** lib/shopify_api/webhooks/registry.rb (L188-200)
```ruby
        sig { params(request: Request).void }
        def process(request)
          raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)

          handler = @registry[request.topic]&.handler

          unless handler
            raise Errors::NoWebhookHandler, "No webhook handler found for topic: #{request.topic}."
          end

          handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop,
            body: request.parsed_body, api_version: request.api_version, webhook_id: request.webhook_id))
        end
```
