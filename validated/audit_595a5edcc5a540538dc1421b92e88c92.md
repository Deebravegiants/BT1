### Title
Webhook `shop-domain` header is trusted for tenant attribution without being covered by the HMAC signature, allowing cross-tenant webhook spoofing - (`lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body [1](#0-0) , so `Utils::HmacValidator.validate` in `Registry.process` only proves that the body bytes were signed with the app secret [2](#0-1) . The `shop`, `topic`, `api_version`, and `webhook_id` values are read straight from unauthenticated HTTP headers [3](#0-2)  and passed to the handler as the tenant identity (`WebhookMetadata.new(topic: request.topic, shop: request.shop, ...)`) without any binding to the signed payload [4](#0-3) .

### Finding Description
The invariant the gem is supposed to enforce is: `shop-in-signed-payload == shop-used-for-tenant-attribution`. Instead, only the body is HMAC-verified, while `shop` is taken from a header that is never mixed into `to_signable_string`. This is the same class of bug as the `poke()` report: a value that influences downstream accounting/attribution (`_pool` weight there, `shop` tenant here) is not covered by the check that is supposed to secure it (`_totalVoteWeight` check there, HMAC signature here), so an attacker who controls the uncovered field can make the system treat data as belonging to a different identity than the one that actually produced/signed it.

Concretely: any developer/tester who has legitimately installed the app on their own store (Shop A) will receive genuine webhook deliveries with a valid HMAC computed over the JSON body using the app's real secret. Because the HMAC does not cover the `shop-domain` header, that attacker can capture one such legitimate `(raw_body, hmac)` pair and replay it to the app's public webhook endpoint while substituting the `x-shopify-shop-domain` header with a victim shop's domain (Shop B). `HmacValidator.validate` still returns `true`, because `verifiable_query.to_signable_string` is unchanged (still `@raw_body`) [5](#0-4) . `Registry.process` then invokes the host application's handler with `shop: "shop-b.myshopify.com"` even though the payload was never produced by or for Shop B [2](#0-1) .

### Impact Explanation
Host applications built on top of this gem are expected to use `WebhookMetadata#shop` to look up the tenant record (merchant) whose data the webhook body should be applied to — that is the entire purpose of exposing `shop` on the metadata object. Since this gem supplies an unauthenticated `shop` value while asserting the body is "verified," any app that trusts it (as the gem's own API surface encourages) can have attacker-controlled event data attributed to, and processed against, a different merchant's tenant than the one that actually signed the request. This is a cross-tenant data-integrity break rooted entirely in this gem's `HmacValidator`/`Webhooks::Request` design, not in host-application misuse of an undocumented contract — the gem documents `shop` as reliable webhook metadata.

### Likelihood Explanation
Exploitability only requires an actor to run the app on one shop they legitimately control (a very low bar — any developer/trial account) and to be able to send a single crafted HTTP POST to the app's public webhook endpoint with an altered header — no `client_secret`, access token, or credential theft is required. The HMAC check still passes because the header is outside its scope, so likelihood is high for any app that keys tenant lookups off `WebhookMetadata#shop`.

### Recommendation
Include the `shop-domain` (and ideally `topic`, `api-version`, `webhook-id`) header values in the signable string used by `Webhooks::Request#to_signable_string`, or otherwise cryptographically bind the header-derived `shop` to the verified body before constructing `WebhookMetadata`, so that `HmacValidator.validate` proves the *entire* tuple `(shop, topic, body)` was produced by Shopify for the claimed tenant rather than just the raw bytes.

### Proof of Concept
1. Install the app on an attacker-controlled shop (`attacker-shop.myshopify.com`) and capture a legitimate webhook delivery: raw body `B` and header `x-shopify-hmac-sha256: H`, where `H = HMAC-SHA256(secret, B)`.
2. Replay the request to the app's webhook endpoint, keeping `raw_body = B` and `x-shopify-hmac-sha256 = H` unchanged, but set `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `Utils::HmacValidator.validate(request)` computes `compute_signature(request.to_signable_string, secret)` — since `to_signable_string` is `@raw_body = B`, the computed signature equals `H`, so validation succeeds [6](#0-5) [1](#0-0) .
4. `Registry.process` calls the handler with `shop: "victim-shop.myshopify.com"` and the attacker's body content, even though the body was never generated for that shop [7](#0-6) .

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-33)
```ruby
      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
      end

      sig { returns(String) }
      def api_version
        T.cast(shopify_header("api-version"), String)
      end

      sig { returns(String) }
      def webhook_id
        T.cast(shopify_header("webhook-id"), String)
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L35-38)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
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
