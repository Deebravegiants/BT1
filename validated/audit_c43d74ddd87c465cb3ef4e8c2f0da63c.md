### Title
Webhook `shop` domain is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable string from the raw body only, while `shop`, `topic`, `webhook_id`, and `api_version` are read directly from unauthenticated HTTP headers and passed downstream to the registered handler as if they were verified. This breaks the identity binding `shop (validated by HMAC) == shop (delivered to handler)`.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop`, `topic`, `webhook_id`, and `api_version` are all read straight from client-supplied HTTP headers, none of which are folded into the signable string: [2](#0-1) 

`Registry.process` validates the HMAC against the body only, then forwards the unauthenticated `request.shop` (and other header-derived fields) to the app's handler: [3](#0-2) 

Because `HmacValidator.validate` (`lib/shopify_api/utils/hmac_validator.rb:12-31`) only proves that the *body bytes* were signed with the app's `api_secret_key` — it says nothing about which shop the body belongs to — any party who can obtain one valid `(raw_body, hmac)` pair for the app's secret (e.g. by owning a shop that has the app installed and observing its own real webhook deliveries, which is not a privileged action) can replay that exact body+HMAC pair to the app's webhook endpoint while substituting an arbitrary `x-shopify-shop-domain` header. The `HmacValidator` will report the request as valid, and `WebhookMetadata.shop` will contain the attacker-chosen shop domain rather than the shop that actually produced the body. [4](#0-3) 

This is exactly the class of bug described by the analog rule: "a field acted on but not covered by the HMAC" — here the `shop` field used downstream for tenant attribution is not part of the HMAC-covered material, even though the surrounding API (`Registry.process`, `WebhookMetadata`) treats HMAC success as proof the entire request, including `shop`, is authentic.

### Impact Explanation
Any app built on this gem that uses `WebhookMetadata#shop` from a successfully-validated webhook to select, index, or mutate per-tenant state (session lookup, order/customer records, feature flags, etc.) can be made to attribute a replayed payload to a victim shop chosen by the attacker. This is a cross-tenant confusion/access primitive: data or side effects intended for shop A can be forced onto shop B's tenant context using only a body+HMAC pair the attacker legitimately observed from their own installation — no access token, `client_secret`, or privileged account for the victim is required.

### Likelihood Explanation
Exploitation requires the attacker to possess one valid `(raw_body, hmac)` pair signed with the app's shared secret. This is trivially obtainable by any merchant who installs the app (an unprivileged action) and inspects a webhook delivery to their own shop, since `raw_body` and its HMAC are visible to the receiving endpoint operator/merchant infrastructure. No brute force of `api_secret_key` is needed. The only extra step is sending an HTTP POST to the app's webhook route with a swapped `x-shopify-shop-domain` (and, if desired, `x-shopify-topic`/`x-shopify-webhook-id`) header — both trivial for an internet-reachable HTTP client.

### Recommendation
Include the identity-binding headers (`shop`, `topic`, and ideally `webhook_id`) in the value that is HMAC-verified, or otherwise cryptographically bind them to the signed body (e.g., verify the shop domain against session/store state expected for the topic instead of trusting the header verbatim). At minimum, the gem should not let `Registry.process` implicitly attest that `request.shop`/`request.topic` are authenticated just because `Utils::HmacValidator.validate` returned true — documentation and/or an API change should make clear that HMAC validation only certifies the body, and callers must independently authenticate the shop associated with a webhook (e.g., by checking it against a shop that has an active, previously-established session/installation).

### Proof of Concept
1. Attacker installs the target app on their own shop `attacker.myshopify.com` (no special privilege required — any merchant can do this for a public app).
2. Shopify (or the app's own test tooling) delivers a legitimate webhook to the app's endpoint with headers:
   - `x-shopify-shop-domain: attacker.myshopify.com`
   - `x-shopify-hmac-sha256: <valid HMAC of body B>`
   - body `B`
3. Attacker replays the exact same body `B` and `x-shopify-hmac-sha256` value to the same endpoint, but rewrites the header to `x-shopify-shop-domain: victim.myshopify.com`.
4. `Utils::HmacValidator.validate` recomputes the HMAC over `B` only (`Webhooks::Request#to_signable_string` at `lib/shopify_api/webhooks/request.rb:35-38`) and it matches, so `Registry.process` proceeds and invokes the handler with `WebhookMetadata.new(shop: "victim.myshopify.com", ...)` (`lib/shopify_api/webhooks/registry.rb:198-199`), even though the body never actually originated from `victim.myshopify.com`.

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

**File:** lib/shopify_api/webhooks/request.rb (L35-43)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end

      sig { returns(T::Hash[String, T.untyped]) }
      def parsed_body
        JSON.parse(@raw_body)
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
