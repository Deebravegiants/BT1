Confirmed: `Utils::HmacValidator.validate` (via `VerifiableQuery#to_signable_string`) covers only `@raw_body` for webhook requests — the `shop-domain`, `topic`, `webhook-id`, and `api-version` values are read straight from HTTP headers with zero cryptographic binding to that signature.

### Title
Webhook HMAC signs only the request body, letting any sender forge the `shop`, `topic`, and `webhook_id` identity fields trusted by handlers - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`, and `Registry.process` accepts the request purely based on `Utils::HmacValidator.validate(request)` succeeding against that body. The `shop`, `topic`, `webhook_id`, and `api_version` values consumed by the app (and forwarded into `WebhookMetadata`) come straight from HTTP headers that are never included in the signed material.

### Finding Description
`Utils::HmacValidator.validate_signature` computes `OpenSSL::HMAC.hexdigest(sha256, secret, verifiable_query.to_signable_string)` and compares it to the received `hmac`. [1](#0-0) 
For webhooks, `to_signable_string` is defined as just the raw body: [2](#0-1) 
Meanwhile `shop`, `topic`, `webhook_id`, and `api_version` are all pulled from headers that are not part of the signed string: [3](#0-2) 
`Registry.process` treats a passing HMAC check as sufficient authorization to trust *all* of these header-derived fields and dispatches them to the app's handler as authenticated metadata: [4](#0-3) 

Because the HMAC secret (`Context.api_secret_key`) is the app's single client secret shared across every installed shop, any merchant that installs the app can legitimately trigger a webhook to their own endpoint and obtain a `(raw_body, hmac)` pair that is valid under that secret. Nothing then stops that same actor from POSTing the identical body/hmac pair to the app's webhook endpoint with `x-shopify-shop-domain` rewritten to a victim shop's domain, `x-shopify-topic` rewritten to any topic the app has registered a handler for (including the mandatory `customers/redact`, `shop/redact`, `customers/data_request` topics), and `x-shopify-webhook-id` set arbitrarily. `Utils::HmacValidator.validate` returns `true` because it only ever re-derives the signature from `raw_body`, so the forged headers pass unnoticed straight into `WebhookMetadata.new(topic:, shop:, body:, ...)`.

The equality this breaks: `hmac-authenticated bytes (raw_body)` != `identity fields the app trusts (shop, topic, webhook_id)`. The gem lets the shop/topic that the handler believes it received diverge from the shop/topic that Shopify actually signed the payload for.

### Impact Explanation
This is a cross-tenant identity-binding break at the gem's webhook-verification boundary: an app built on this library cannot distinguish "this payload really came from shop X for topic Y" from "an attacker who owns any installation replayed a captured body under a forged shop/topic header." Any host application that (as documented/intended) trusts `WebhookMetadata#shop`/`#topic` once `Registry.process` succeeds — e.g. to look up/update per-shop data, or to react to mandatory compliance topics like `customers/redact` — can be made to act on behalf of, or against, a shop the attacker doesn't control. This satisfies the "cross-tenant access" criterion.

### Likelihood Explanation
Any unprivileged user who can install the app on a store they control (a standard, low-privilege capability for any Shopify Partner/dev account) can capture one legitimate webhook delivery from their own shop and immediately obtain a body+HMAC pair valid for arbitrary header spoofing — no access token, secret, or privileged account is required.

### Recommendation
Include the identity-bearing headers (`shop-domain`, `topic`, `webhook-id`, `api-version`) in the HMAC-signed material, or otherwise cryptographically bind them (e.g., by having `Utils::HmacValidator` verify a canonical string built from headers + body, similar to how `Oauth::AuthQuery#to_signable_string` binds all relevant fields) so a signature computed for one shop/topic cannot be replayed under a different one.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com`.
2. Attacker triggers any subscribed webhook topic (or a mandatory topic like `customers/redact`) and captures the raw POST: body `B` and header `x-shopify-hmac-sha256: H`, where `H = HMAC-SHA256(api_secret_key, B)`.
3. Attacker replays the request to the app's webhook endpoint, keeping `B` and `H` unchanged but setting:
   - `x-shopify-shop-domain: victim-shop.myshopify.com`
   - `x-shopify-topic: customers/redact` (or any other registered topic)
   - `x-shopify-webhook-id: <arbitrary>`
4. `Utils::HmacValidator.validate` recomputes the HMAC over `B` only, finds it matches `H`, and returns `true`. [5](#0-4) 
5. `Registry.process` proceeds and invokes the registered handler with `WebhookMetadata.new(topic: "customers/redact", shop: "victim-shop.myshopify.com", body: <attacker-controlled>, ...)`, even though Shopify never sent this payload for `victim-shop`. [4](#0-3)

### Citations

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
