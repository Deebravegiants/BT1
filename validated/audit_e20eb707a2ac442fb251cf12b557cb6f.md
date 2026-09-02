## Title
Webhook HMAC only signs the request body, not the `shop`/`topic`/`webhook-id` headers, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` accepts any webhook request whose HMAC matches the **raw body**, then blindly forwards the unauthenticated `shop`, `topic`, `webhook_id`, and `api_version` header values to the app's handler as if they were verified. Because the HMAC signature never covers these header fields, an attacker who legitimately receives one real webhook (e.g. from their own free dev store) can replay it to the app's public webhook endpoint with the `x-shopify-shop-domain` header rewritten to any other shop, and the signature check still succeeds.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

while `shop`, `topic`, `webhook_id`, and `api_version` are read straight from HTTP headers with no cryptographic binding to the signature: [2](#0-1) 

`Registry.process` validates the HMAC and then uses the unauthenticated `request.shop` (and topic/webhook_id/api_version) directly to build the data handed to the app's handler: [3](#0-2) 

The identity binding broken here is: **shop authenticated by HMAC ("`raw_body`") ≠ shop acted on by the handler ("`request.shop` header")**. `Utils::HmacValidator.validate` only proves "this body was produced with our `api_secret_key`" — it proves nothing about which shop the request claims to be from: [4](#0-3) 

### Impact Explanation
An attacker who installs the app on their own (even free/dev) store receives real, correctly-signed webhooks for that store. Since the signature only covers the body, the attacker can replay that exact HTTP request straight to the app's public webhook endpoint while changing only `x-shopify-shop-domain` (and/or `x-shopify-topic`/`x-shopify-webhook-id`) to point at a victim shop. `Registry.process` will pass the HMAC check (body unchanged) and dispatch to the handler with `WebhookMetadata#shop` set to the victim's domain while `body` contains attacker-controlled/attacker-owned data. If the host app trusts `data.shop` to key its per-tenant session/data store (the documented and intended usage pattern of `WebhookMetadata`), this results in cross-tenant data injection/corruption — the exact "shop authenticated versus shop acted on" boundary break called out as in-scope.

### Likelihood Explanation
No privileged credentials, access token, or `api_secret_key` knowledge is required. Any unprivileged internet user can install the target app on a store they control (or use an existing legitimate webhook they've received) and directly POST the replayed payload to the app's public webhook route with a forged shop header — the gem performs no defense against this because it never binds the header claims to the signature.

### Recommendation
Bind the shop/topic/webhook-id to the signed material, or require the caller to independently verify `request.shop` against a known/registered shop (e.g., cross-check against an active session or installed-shop list) before trusting it, rather than deriving tenant identity purely from an unauthenticated header. At minimum, document prominently that `WebhookMetadata#shop`/`#topic`/`#webhook_id` are **not** authenticated by the HMAC check and must not be used as a trusted tenant key without additional verification.

### Proof of Concept
1. Install the app on attacker-controlled shop `attacker.myshopify.com`; trigger any webhook (e.g. `orders/create`) and capture the raw POST: body `B`, headers including `x-shopify-hmac-sha256: H` (valid HMAC of `B`) and `x-shopify-shop-domain: attacker.myshopify.com`.
2. Replay the exact same body `B` and HMAC header `H` to the app's public webhook endpoint, but set `x-shopify-shop-domain: victim.myshopify.com`.
3. `Utils::HmacValidator.validate` succeeds (it only checks `B` against `H`) per `lib/shopify_api/utils/hmac_validator.rb`.
4. `Registry.process` builds `WebhookMetadata.new(shop: "victim.myshopify.com", body: <attacker's own order data>, ...)` per `lib/shopify_api/webhooks/registry.rb` lines 188-200, and the app's handler executes as if this event genuinely belongs to `victim.myshopify.com`.

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
