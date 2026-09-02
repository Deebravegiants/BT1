This confirms the finding. The webhook HMAC in `ShopifyAPI::Webhooks::Request#to_signable_string` (`lib/shopify_api/webhooks/request.rb:36-38`) only signs `@raw_body`, while `shop`, `topic`, `webhook_id`, and `api_version` are read straight from unauthenticated HTTP headers (lines 15-33) and passed unbound into the handler by `Registry.process` (`lib/shopify_api/webhooks/registry.rb:189-199`).

### Title
Webhook `shop` (tenant) identity is not bound to the HMAC signature, allowing cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` verifies webhook authenticity via `Utils::HmacValidator.validate(request)`, but the HMAC is computed only over the raw request body (`to_signable_string` returns `@raw_body`). The `shop`, `topic`, `webhook_id`, and `api_version` values used by `Registry.process` to dispatch and label the webhook are read from HTTP headers (`x-shopify-shop-domain`, `x-shopify-topic`, etc.) that are never included in the signed bytes. [1](#0-0) [2](#0-1) 

### Finding Description
`Utils::HmacValidator.validate` computes `compute_signature(verifiable_query.to_signable_string, secret)` and compares it against the received `hmac` value using `OpenSSL.secure_compare`. [3](#0-2) 

For webhook requests, `to_signable_string` returns only `@raw_body`, and `hmac` is parsed from the `x-shopify-hmac-sha256` header — but `shop`, `topic`, `webhook_id`, and `api_version` are all parsed directly from attacker-controllable headers, entirely outside the signed payload: [4](#0-3) 

`Registry.process` trusts these unsigned header-derived fields to select the handler and to populate the `WebhookMetadata` passed to the app's webhook handler, including `shop: request.shop`: [2](#0-1) 

The identity binding that should hold is: `HMAC_valid(body, secret) == true` should imply `shop_header == shop_that_actually_sent_this_body`. In this implementation, `HMAC_valid` is computed purely as a function of `body` and `secret`, independent of `shop`/`topic`/`webhook_id` — so those fields are verified against nothing. Any request carrying a `(body, hmac)` pair that was ever validly produced by Shopify for the app's secret (e.g., a webhook delivery to the app's own endpoint, which any merchant installing the app can trigger for their own shop) passes HMAC validation regardless of which `shop-domain`/`topic`/`webhook-id` header accompanies it on replay.

### Impact Explanation
This breaks the tenant (shop) identity binding for webhook delivery. An attacker who operates their own Shopify store with the same app installed can capture a legitimate `(raw_body, hmac)` pair from a webhook delivered to their own store, then replay it to the same endpoint with a forged `x-shopify-shop-domain` header pointing at a victim shop. Because `HmacValidator.validate` never binds `shop` to the signature, the request passes validation, and the app's webhook handler receives `WebhookMetadata` claiming the event/body belongs to the victim shop. If the host app uses `shop` from `WebhookMetadata` to look up per-tenant state, credentials, or to perform tenant-scoped writes (the documented and expected usage pattern for `ShopifyAPI::Webhooks::WebhookMetadata`), this results in cross-tenant data confusion/access — a Critical-impact class per the scope rules.

### Likelihood Explanation
Likelihood is meaningful but bounded: the attacker must be able to obtain at least one valid `(body, hmac)` pair signed with the app's secret, which any merchant who installs the app and receives webhooks for their own shop can do trivially (no `api_secret_key` leak required — they only replay what Shopify already sent them). They then only need to modify the header they control on their own HTTP replay to the app's public webhook endpoint. No access token, refresh token, or `client_secret` theft is needed to mount this — it purely exploits the missing binding in `to_signable_string`/`HmacValidator`.

### Recommendation
Include `shop`, `topic`, and `webhook_id`/`api_version` in the signed material used for HMAC validation, or otherwise cryptographically bind the tenant identity to the payload — e.g., verify that `shop` matches an expected/stored value for the specific webhook subscription (webhook_id) rather than trusting the header verbatim, and document that `Registry.process`/`WebhookMetadata` should not be treated as tenant-authenticated purely because `HmacValidator.validate` returned `true`. At minimum, update `to_signable_string` in `lib/shopify_api/webhooks/request.rb` to incorporate the shop/topic headers into the signable bytes (matching how `Auth::Oauth::AuthQuery#to_signable_string` binds `shop` into its signed string) so the HMAC check enforces `shop` integrity, not just body integrity.

### Proof of Concept
1. Attacker installs the app on their own store `attacker.myshopify.com` and triggers any webhook topic (e.g., `orders/create`), receiving a legitimate delivery with headers `x-shopify-shop-domain: attacker.myshopify.com`, `x-shopify-topic: orders/create`, `x-shopify-hmac-sha256: <valid-hmac-of-body>`, and body `B`.
2. Attacker replays the exact same body `B` and `hmac` value to the app's webhook endpoint, but changes the header to `x-shopify-shop-domain: victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which only checks `HMAC(secret, B) == received_hmac` — this still passes since `B` and the hmac are unchanged. [5](#0-4) 
4. The handler is invoked with `WebhookMetadata.new(topic: request.topic, shop: "victim.myshopify.com", body: ..., ...)`, i.e., the app now believes this webhook body legitimately originated from `victim.myshopify.com`. [6](#0-5)

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-38)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end

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
