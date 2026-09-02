### Title
Webhook `shop` identity is trusted without being covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by verifying an HMAC over the raw request body, but the `shop` value that is subsequently handed to the app's webhook handler as the tenant identifier is taken from an HTTP header that is never included in that HMAC computation. This breaks the intended binding `HMAC-verified bytes == tenant identity used by the handler`.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`ShopifyAPI::Utils::HmacValidator.validate` computes the HMAC exclusively over `verifiable_query.to_signable_string` (i.e., the body) and compares it to the `hmac` value: [2](#0-1) 

`Registry.process` treats a passing HMAC check as proof of authenticity for the whole request, then immediately reads `request.shop` — sourced from the unauthenticated `shopify-shop-domain`/`x-shopify-shop-domain` header — and forwards it to the app's handler as the tenant identity: [3](#0-2) [4](#0-3) 

Contrast this with `ShopifyAPI::Auth::Oauth::AuthQuery`, where `shop` **is** included in the signable string used for OAuth callback HMAC verification: [5](#0-4) 

Because a single app-wide `api_secret_key` is used to sign webhooks for *every* installed shop (this is standard Shopify behavior, not specific to a merchant), and the signature covers only the body, an attacker who controls one legitimate installation (Shop A) can capture a real, validly-signed webhook payload for Shop A and replay it to the app's webhook endpoint with the `shop-domain` header rewritten to Shop B. `HmacValidator.validate` will still pass because it never inspected the shop header, and `Registry.process` will hand the handler a `WebhookMetadata` claiming `shop: "shop-b.myshopify.com"` with Shop-A-controlled body content.

The equality broken: `bytes verified by HMAC == identity field trusted by the handler` — the HMAC verifies `raw_body` only, while `request.shop` (unauthenticated) is what the handler uses to decide which tenant's data to update.

### Impact Explanation
If an app's webhook handler uses `data.shop` (from `WebhookMetadata`) to look up or mutate per-tenant records — the documented and expected usage pattern — an attacker with access to one Shopify store's legitimate webhook stream can forge webhook deliveries that are misattributed to a different, victim shop. Depending on the handler's logic, this can lead to cross-tenant data corruption, cross-tenant data disclosure, or business-logic manipulation for a shop the attacker does not control, without needing that shop's access token or secret. This matches the Critical "cross-tenant access" impact category since the trust boundary between tenants inside a single app is broken using only unprivileged access to a webhook feed for one's own store.

### Likelihood Explanation
Exploitation requires: (1) the attacker operates or controls at least one shop with the app installed so they can obtain a validly-HMAC-signed webhook body for a topic of interest, and (2) the ability to POST arbitrary headers to the app's public webhook endpoint (which is by definition internet-reachable and unauthenticated other than via this HMAC check). Both conditions are realistic for any attacker who installs the target app on a store they control — no privileged credentials, access tokens, or `client_secret` are needed. Likelihood is therefore Medium-High for any app relying on `request.shop`/`WebhookMetadata#shop` for tenant scoping, which is the intended and documented usage.

### Recommendation
Bind the shop identity to the signed payload rather than trusting an out-of-band header:
- Extract the shop from the webhook payload's own signed content where the topic includes it, or
- Require the gem to fold the `shop-domain` header into the HMAC signable string (mirroring `AuthQuery#to_signable_string`), rejecting requests where the header does not match what was signed, or
- At minimum, cross-check `request.shop` against the shop associated with the resource IDs inside the (HMAC-covered) body before dispatching to the handler, and clearly document that `WebhookMetadata#shop` is not itself authenticated by the HMAC so integrators do not rely on it as a trust boundary.

### Proof of Concept
1. App is installed on attacker-controlled `shop-a.myshopify.com`; attacker triggers a webhook topic (e.g., `orders/create`) and captures the raw POST: headers (`x-shopify-hmac-sha256: <valid-hmac-for-body>`, `x-shopify-shop-domain: shop-a.myshopify.com`, `x-shopify-topic: orders/create`) and body `B`.
2. Attacker replays the exact same body `B` and `x-shopify-hmac-sha256` value to the app's public webhook endpoint, but changes `x-shopify-shop-domain` to `shop-b.myshopify.com`.
3. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which only hashes `request.to_signable_string` (`= B`) — unchanged — so the check passes: [6](#0-5) 
4. The handler receives `WebhookMetadata.new(topic: "orders/create", shop: "shop-b.myshopify.com", body: parsed(B), ...)` and performs tenant-scoped actions against Shop B's data using attacker-supplied body content, even though Shop B never sent this webhook.

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

**File:** lib/shopify_api/webhooks/registry.rb (L188-199)
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
```

**File:** lib/shopify_api/auth/oauth/auth_query.rb (L33-43)
```ruby
        sig { override.returns(String) }
        def to_signable_string
          params = {
            code: code,
            host: host,
            shop: shop,
            state: state,
            timestamp: timestamp,
          }
          URI.encode_www_form(params)
        end
```
