Found: the webhook HMAC signature covers only the raw request body, while the `shop` used to key the callback (`request.shop`, which becomes `WebhookMetadata#shop` passed to the handler) is taken directly from the unauthenticated `x-shopify-shop-domain` / `shopify-shop-domain` header.

### Title
Webhook `shop` identity is not covered by the HMAC signature, allowing tenant spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) , while `Registry.process` uses `Utils::HmacValidator.validate(request)` to authenticate the request and then trusts `request.shop`, read straight from the `shopify-shop-domain`/`x-shopify-shop-domain` header, as the tenant identity passed into the handler [2](#0-1) [3](#0-2) .

### Finding Description
This mirrors the report's bug class: a value used for a security decision (here, tenant/shop identity) is not covered by the same integrity check that is used to "prove" the request is legitimate (here, HMAC), analogous to the 1inch check validating total balance instead of the balance delta actually produced by the verified action. `Utils::HmacValidator.validate` computes and compares the HMAC only over `verifiable_query.to_signable_string`, which for `Webhooks::Request` is exactly the raw body bytes [4](#0-3) [1](#0-0) . The `shop` header is never mixed into that signable string, so the equality the gem should enforce — "shop that was HMAC-authenticated" == "shop passed to the handler" — does not actually hold; only "body bytes HMAC-authenticated" == "body bytes parsed" holds.

### Impact Explanation
An app receiving webhooks through this library, if it relies on `WebhookMetadata#shop` for tenant scoping (e.g., looking up which merchant's data/record the body pertains to, or logging/attribution), can be made to process an HMAC-valid body under an attacker-chosen shop identity, since only `client_secret` is required to sign an arbitrary body, but nothing binds that signed body to a specific shop domain header. This is a cross-tenant identity-binding break at the gem level: the primitive it exposes (`Registry.process`/`WebhookMetadata`) hands the host app a `shop` value with no cryptographic connection to the payload it approved.

### Likelihood Explanation
Exploiting this still requires the ability to send a request with a valid HMAC for the chosen body (i.e., knowledge of `client_secret`, same as for legitimate Shopify webhooks) — so it does not enable an unprivileged internet user to forge whole webhooks from scratch. However, given a legitimately captured or replayable HMAC-signed body (e.g., replaying a benign webhook body signed for one topic/shop, or an app that logs/echoes bodies), an attacker can freely swap the `x-shopify-shop-domain` header to any value while keeping the signature and body intact, since that header carries no cryptographic binding. This is a real gap in the gem's own webhook-authenticity contract, independent of any misuse by the host app.

### Recommendation
Include `shop`, `topic`, and `webhook_id` (or at minimum `shop`) in the HMAC signable string, or otherwise require the host application to independently corroborate the shop identity against a value it already trusts (e.g., the shop associated with the webhook subscription being delivered) rather than trusting the unauthenticated header value outright. At minimum, document clearly that `WebhookMetadata#shop` is not authenticated by the HMAC check and must not be used for authorization decisions without additional verification.

### Proof of Concept
1. Attacker who possesses a validly HMAC-signed webhook body/signature pair for `raw_body = B` (signed with the app's `client_secret`) can construct a new request:
   - `headers["x-shopify-hmac-sha256"] = <same HMAC>` 
   - `headers["x-shopify-shop-domain"] = "victim-shop.myshopify.com"` (attacker-chosen, arbitrary)
   - `raw_body = B` (unchanged)
2. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks `B` against the HMAC [5](#0-4) .
3. `handler.handle(data: WebhookMetadata.new(..., shop: request.shop, ...))` is invoked with `shop = "victim-shop.myshopify.com"`, a value fully controlled by the attacker and never checked against the signed content [6](#0-5) .

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-22)
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
