### Title
Webhook `shop-domain`, `topic`, and `webhook-id` headers are not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable content from the raw body only, while the `shop`, `topic`, `webhook_id`, and `api_version` values that `Registry.process` hands to application webhook handlers are read from unauthenticated HTTP headers. Any party who can obtain one valid `(body, hmac)` pair signed with the app's shared `api_secret_key` can replay that body against the app's public webhook endpoint while freely substituting the `shop-domain` header, causing the app to process attacker-controlled data under a victim shop's identity.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

Meanwhile `shop`, `topic`, `webhook_id`, and `api_version` are pulled straight from headers with no cryptographic binding to the signature: [2](#0-1) 

`Registry.process` verifies only the body-derived HMAC and then trusts `request.shop`/`request.topic` verbatim when dispatching to the app's handler: [3](#0-2) 

`HmacValidator.validate` performs a straightforward `OpenSSL.secure_compare` over `compute_signature(verifiable_query.to_signable_string, secret)`, so it only ever attests to the body, never to which shop or topic the payload is claimed to belong to: [4](#0-3) 

The identity binding that should hold is:
`HMAC(secret, signed_bytes)` valid ⇒ `signed_bytes` include `shop` ⇒ `data.shop` passed to the handler is authentic.

In this implementation, `signed_bytes == raw_body` only, so the equality `HMAC-valid ⇒ shop authentic` does not hold: `shop` is acted upon (used to build `WebhookMetadata` and dispatched to the handler) but is not part of what the HMAC covers.

Because every webhook this app's `api_secret_key` will ever sign uses the *same* shared secret regardless of which shop triggered it, any user who can install the app on a shop they control (or otherwise obtain a legitimately-signed webhook body, e.g. from their own store's webhook deliveries) can capture a valid `(raw_body, X-Shopify-Hmac-Sha256)` pair. They can then POST that exact body and signature straight to the app's public webhook endpoint themselves, substituting `X-Shopify-Shop-Domain` (and optionally `X-Shopify-Topic`) with an arbitrary victim shop. `Utils::HmacValidator.validate` will report success because the HMAC only ever attested to the body content, and `Registry.process` will hand the handler a `WebhookMetadata` claiming the (attacker-controlled) body belongs to the victim shop.

### Impact Explanation
This breaks the shop/tenant identity binding that webhook handlers rely on to know which merchant's data they are processing. Any host application logic that uses `WebhookMetadata#shop` to select which tenant's records to create/update/delete (a standard and expected usage pattern for Shopify apps) can be tricked into attributing attacker-chosen payload content to a shop the attacker does not control — a cross-tenant data-integrity/spoofing issue reachable by any unprivileged internet user who can install the app on any store (including a free/dev store) to harvest one valid signed payload.

### Likelihood Explanation
Likelihood is moderate-to-high for apps that expose their webhook endpoint publicly (which is required for Shopify webhook delivery). Obtaining a valid `(body, hmac)` pair requires only installing the app on a store the attacker controls and triggering the relevant webhook topic (e.g. `products/create`), both of which are self-service actions requiring no privileged Shopify or app-owner credentials. No `client_secret` or access token needs to be leaked — the vulnerability lies entirely in this gem not binding `shop`/`topic` into the signed content.

### Recommendation
Include the `shop-domain`, `topic`, `webhook-id`, and `api-version` header values in the material that is HMAC-verified (or otherwise cryptographically bind them to the request), rather than trusting them as independent, unauthenticated headers once the body-only HMAC passes. At minimum, document that host applications must not trust `WebhookMetadata#shop`/`#topic` without independently corroborating them (e.g., checking that the shop is one the app has an active session for and matches the topic/resource actually referenced in the body).

### Proof of Concept
1. Install the app under test on an attacker-controlled shop `attacker.myshopify.com` and let Shopify deliver a legitimate webhook, e.g. `products/create`, to the app's public webhook endpoint. Capture the raw request: body `B` and header `X-Shopify-Hmac-Sha256: H` (computed as `HMAC-SHA256(api_secret_key, B)`, matching `Request#to_signable_string`/`#hmac`).
2. Send a new POST directly to the same webhook endpoint with:
   - Body: the identical `B`
   - `X-Shopify-Hmac-Sha256: H` (unchanged, still valid because it only ever signed `B`)
   - `X-Shopify-Shop-Domain: victim.myshopify.com` (replacing the attacker's own domain)
   - `X-Shopify-Topic`, `X-Shopify-Webhook-Id`, `X-Shopify-Api-Version` left as convenient
3. `Utils::HmacValidator.validate(request)` returns `true` because `compute_signature` only ever hashed `B` (`lib/shopify_api/webhooks/request.rb` lines 35-38, `lib/shopify_api/utils/hmac_validator.rb` lines 26-31).
4. `Registry.process` dispatches to the registered handler with `WebhookMetadata.new(topic: ..., shop: "victim.myshopify.com", body: JSON.parse(B), ...)` (`lib/shopify_api/webhooks/registry.rb` lines 188-199), causing the host app to act on attacker-controlled body content as though it were legitimately reported by `victim.myshopify.com`.

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
