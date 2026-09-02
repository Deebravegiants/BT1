### Title
Webhook shop-domain header is not covered by HMAC verification, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/utils/hmac_validator.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by HMAC-verifying the raw request body against the app's single, shop-independent `api_secret_key`. The `shop-domain` header — which is handed to the app's handler as the authoritative tenant identifier — is never included in the signed material. Because the same `api_secret_key` is used for every shop that has the app installed, any party that can obtain one valid `(body, hmac)` pair (e.g. by triggering a webhook on their own installed shop) can replay that exact body with an arbitrary `shop-domain` header to the app's public webhook endpoint and have it accepted as an authentic webhook "from" a different, victim shop.

### Finding Description
`Request#to_signable_string` returns only the raw body: [1](#0-0) 

`request.shop` is read straight from the `shopify-shop-domain` / `x-shopify-shop-domain` header with no cryptographic binding: [2](#0-1) 

`HmacValidator.validate` computes and compares the signature over `verifiable_query.to_signable_string` only — i.e. the body — using the app's global `Context.api_secret_key`: [3](#0-2) 

`Registry.process` treats a passing HMAC check as full authentication of the request and then forwards the unauthenticated `shop` header value straight to the app's handler: [4](#0-3) 

The identity binding that should hold is: `shop-domain-attributed-to-event == shop-domain-cryptographically-committed-in-signature`. Before the attacker's request, a legitimate webhook has both sides equal (Shopify signs the body and the shop it targets is fixed by Shopify's delivery). After the attacker's replay, the left side becomes the attacker-chosen header value while the right side (what the HMAC actually authenticates) is only the body content — the two are decoupled. Since `api_secret_key` is one shared secret for the whole app across all shop installs (not per-shop), any tenant that can generate one valid signed body (by causing any webhook to fire on their own store, which they legitimately control) can pair that valid `(body, hmac)` with a forged `shop-domain` header naming a different shop, and `HmacValidator.validate` will still return `true`.

### Impact Explanation
Handlers typically use `WebhookMetadata#shop` to identify which tenant's data/session to act on (per the gem's own webhook usage docs). An attacker-controlled `shop` value passed through a "verified" webhook enables cross-tenant confusion: an app could perform shop-scoped actions (e.g., updating stored data, invalidating/mutating per-shop state, writing attacker-supplied `body` content) attributed to a victim shop the attacker never installed the app on. This matches the Critical category "cross-tenant access" — the gem's own HMAC verification, which is the sole authenticity guarantee it provides for webhooks, does not bind the tenant identifier it exposes to callers.

### Likelihood Explanation
Exploitation only requires: (1) attacker has (or creates) any shop with the vulnerable app installed, so they can trigger a legitimate webhook and capture a valid `(raw_body, hmac)` pair, and (2) the app's webhook endpoint is reachable over the internet (a standard requirement for Shopify webhook delivery, and the gem does not require or check any transport-level proof of Shopify origin such as source IP or mTLS). No access token, `client_secret`, or privileged account is needed — the attacker acts purely as an ordinary, small-privilege app installer. This is a straightforward, repeatable replay against the gem's own verification logic.

### Recommendation
Include the shop-identifying and topic-identifying material in the value that is HMAC-verified, or otherwise cryptographically bind the `shop-domain` header to the verified payload before trusting it (e.g., verify the header against a shop the app knows it delivered webhooks to/has an active session for, or require the request to be validated through a Shopify-signed channel that commits to the shop, not just the body). At minimum, document and enforce that `WebhookMetadata#shop` must not be trusted as an authenticated tenant identifier unless additional binding is performed by the caller, and consider incorporating the header set into `to_signable_string` similar to how Shopify's HMAC covers full context in other verification flows (e.g. OAuth's `AuthQuery#to_signable_string`, which does include all relevant fields — see `lib/shopify_api/auth/oauth/auth_query.rb` lines 33-43 — unlike the webhook `Request`).

### Proof of Concept
1. Attacker installs the app on their own shop `attacker.myshopify.com` (or otherwise obtains a legitimate webhook delivery) and captures a valid webhook POST: raw body `B`, header `x-shopify-hmac-sha256: H` (valid for `B` under the app's global `api_secret_key`).
2. Attacker sends a raw HTTP POST directly to the app's webhook route (the same route the app registered for `ShopifyAPI::Webhooks::Registry.process`) with:
   - Body: `B` (unchanged)
   - `x-shopify-hmac-sha256: H` (unchanged, still valid since only body is signed)
   - `x-shopify-shop-domain: victim-shop.myshopify.com` (forged)
   - `x-shopify-topic: <chosen topic>`
3. The app calls `ShopifyAPI::Webhooks::Registry.process(ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: forged_headers))`.
4. `Utils::HmacValidator.validate` returns `true` because it only checks `B` against `H` using `Context.api_secret_key` — the forged `shop-domain` header is never inspected.
5. The registered handler is invoked with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: parsed(B), ...)`, letting the attacker inject arbitrary event data attributed to a shop they do not control.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery).returns(T::Boolean) }
        def validate(verifiable_query)
          return false unless verifiable_query.hmac

          result = validate_signature(verifiable_query, Context.api_secret_key)
          if result || Context.old_api_secret_key.nil? || T.must(Context.old_api_secret_key).empty?
            result
          else
            validate_signature(verifiable_query, T.must(Context.old_api_secret_key))
          end
        end

        private

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
