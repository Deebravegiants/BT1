This confirms the vulnerability. The `WebhookMetadata.shop` field passed to every app's handler is sourced directly from the unauthenticated `x-shopify-shop-domain` header, while the gem's HMAC verification only covers the raw request body.

### Title
Webhook `shop` (and `topic`/`api-version`/`webhook-id`) identity fields are not covered by HMAC verification, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC of the raw HTTP body, then trusts the `shop` (and `topic`) values taken from HTTP headers to build the `WebhookMetadata` that is handed to the app's `WebhookHandler`. Because the shop identity is never included in the signed material, any request with a body/HMAC pair that validates under the app's single, shop-agnostic `client_secret` can be replayed with an arbitrary `shop-domain` header, breaking the binding between "HMAC verified" and "belongs to shop X."

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`, and `hmac` returns the value of the `hmac-sha256` header: [1](#0-0) 

`Utils::HmacValidator.validate` computes the signature purely from `verifiable_query.to_signable_string` (i.e., the raw body) using `Context.api_secret_key`, and never mixes in `shop`, `topic`, `webhook_id`, or `api_version`: [2](#0-1) 

`Registry.process` uses that same-secret-for-all-shops HMAC check as the sole authentication gate, then builds `WebhookMetadata` directly from unauthenticated headers (`request.topic`, `request.shop`, `request.webhook_id`, `request.api_version`) and forwards it to the app's handler as trusted data: [3](#0-2) 

`Webhooks::Request#shop` and `#topic` are read straight from `shopify-shop-domain` / `shopify-topic` headers with no cryptographic binding to the HMAC-signed body: [4](#0-3) 

The identity equality this gem is supposed to enforce is:
`shop_that_produced_the_HMAC-signed_body == shop_attributed_to_the_webhook_in_WebhookMetadata.shop`

Since one app has exactly one `client_secret` shared across all shops that install it, an attacker who legitimately controls (or can trigger events in) any single shop can capture a valid `(raw_body, hmac)` pair for a real webhook delivered to their own shop, then replay that exact body+hmac to the app's webhook endpoint while substituting an arbitrary `x-shopify-shop-domain` header (and/or `x-shopify-topic`). `Utils::HmacValidator.validate` still passes because it only checks the body against the shared secret; `Registry.process` then dispatches to the handler with `WebhookMetadata#shop` set to the attacker-chosen victim shop.

### Impact Explanation
This is a cross-tenant boundary violation: the gem hands the host application webhook data falsely attributed to a shop the attacker does not control, while asserting (via successful HMAC validation) that it is authentic. Any app that uses `WebhookMetadata#shop` to key data writes, sync state, or authorization decisions (a documented and expected usage pattern of this API) can have its per-tenant data integrity corrupted by an unrelated, unprivileged merchant/attacker. This matches the Critical bucket for cross-tenant access.

### Likelihood Explanation
Exploitation requires only: (1) the attacker operates or can induce a webhook-triggering event on any shop that has the target app installed (a normal, unprivileged merchant capability), and (2) the app's webhook endpoint is internet-reachable (a documented requirement for webhook delivery). No access token, secret, or privileged account is needed — the attacker only needs one genuine `(body, hmac)` pair from their own tenant, which they always have by construction.

### Recommendation
Bind the shop (and ideally topic/webhook id) into the material that is cryptographically verified, e.g. by requiring/validating that the webhook's shop matches an expected/registered shop for that delivery, or by including the shop domain and topic in the HMAC input the gem computes over. At minimum, `Registry.process` should not treat header-derived `shop`/`topic` as authenticated identity fields when only the body has been verified — document this explicitly and/or provide a validation hook that lets host apps cross-check `request.shop` against the shop context under which the webhook was registered.

### Proof of Concept
1. App has a single `client_secret` `S`, shared by all installed shops (Shop A - attacker-controlled, Shop B - victim).
2. Attacker triggers an event on Shop A that causes Shopify to deliver a webhook to the app: headers `x-shopify-shop-domain: shop-a.myshopify.com`, `x-shopify-hmac-sha256: <valid-hmac-of-body>`, body `B`.
3. Attacker intercepts/replays this exact `(B, hmac)` pair to the app's webhook endpoint, but rewrites the header to `x-shopify-shop-domain: shop-b.myshopify.com`.
4. `Utils::HmacValidator.validate` (`lib/shopify_api/utils/hmac_validator.rb:12-31`) recomputes the HMAC over `B` using shared secret `S` — it matches, since `shop` was never part of the signed input.
5. `Registry.process` (`lib/shopify_api/webhooks/registry.rb:188-200`) builds `WebhookMetadata.new(shop: "shop-b.myshopify.com", ...)` from the spoofed header and calls `handler.handle(data: ...)`, causing the app to process attacker-supplied body data as though it belongs to Shop B.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-40)
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

        sig { params(signable_string: String, secret: String).returns(String) }
        def compute_signature(signable_string, secret)
          OpenSSL::HMAC.hexdigest(
            OpenSSL::Digest.new("sha256"),
            secret,
            signable_string,
          )
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
