## Finding

### Title
Webhook `shop` identity is taken from an HMAC-unauthenticated header, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb](lib/shopify_api/webhooks/request.rb))

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates a webhook only by validating the HMAC over the raw request body, then hands the handler a `shop` value read from an HTTP header that is never covered by that HMAC. Because the signing secret is the app's single shared `client_secret` (not a per-shop secret), any binding between "this HMAC is valid" and "this event belongs to shop X" is missing, letting an attacker splice a valid `(body, hmac)` pair with an arbitrary `shop-domain` header.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

and `hmac`, `topic`, `shop`, `api_version`, and `webhook_id` are all read straight from HTTP headers that are not part of the signed material: [2](#0-1) 

`Registry.process` validates the request using only this HMAC-over-body check, then immediately trusts `request.shop` (and `request.topic`) to build the object passed to the handler: [3](#0-2) 

`Utils::HmacValidator.validate` computes `HMAC(secret, to_signable_string)`, i.e. `HMAC(secret, raw_body)` — the shop-domain header never enters the computation: [4](#0-3) 

The identity equality that should hold is: `shop authenticated by the HMAC == shop delivered to the handler as WebhookMetadata#shop`. In this implementation that equality does not exist — the HMAC only proves "this body was produced/observed by someone holding the app's `api_secret_key`" (which, for a webhook, is Shopify itself when it sent it the first time), it says nothing about which shop the body pertains to, since `shop` is a header, not part of the signed payload.

Because Shopify signs *all* webhooks for an app with the same shared `api_secret_key` regardless of which shop triggered them, a user who installs the app on their own shop (`attacker-shop.myshopify.com`, no special privileges required — any merchant can install a public app) receives legitimately-signed webhooks. They can capture one such `(raw_body, hmac)` pair from their own shop's webhook deliveries, then replay that exact body and HMAC to the app's webhook endpoint while substituting `x-shopify-shop-domain: victim-shop.myshopify.com`. `HmacValidator.validate` still succeeds (it only checks the body), and `Registry.process` calls the handler with `WebhookMetadata.new(... shop: "victim-shop.myshopify.com", body: <attacker's own body> ...)`.

### Impact Explanation
Any host application that uses `data.shop` from `WebhookMetadata` to select per-tenant records, update per-shop state, or determine authorization (which is the documented and expected usage pattern in `docs/usage/webhooks.md`) can be tricked into applying attacker-controlled webhook content to a victim shop's tenant context, using nothing but a webhook the attacker legitimately received for their own store. This is a cross-tenant access primitive: an unprivileged merchant of the app can inject fabricated events attributed to a different, unrelated merchant, potentially corrupting or exfiltrating cross-tenant application state depending on how the host handles the topic (e.g. billing, order, or uninstall-related topics).

### Likelihood Explanation
Likelihood is high for any attacker who is themselves a legitimate (if unprivileged) installer of the target app: no secrets, tokens, or privileged access are required beyond installing the app on a shop they control and being able to send arbitrary HTTP requests (headers are fully attacker-controlled) to the app's public webhook endpoint.

### Recommendation
Bind the authenticated identity to the HMAC. Either include the shop domain (and topic) inside the signed material presented to `HmacValidator`, or require the host application to independently verify that the `shop` header corresponds to a shop with a currently stored, valid session/access token before trusting `WebhookMetadata#shop`; the library should surface this requirement explicitly (e.g., by making `Registry.process` accept/require a shop-verification callback) rather than treating header-derived `shop` as authenticated once `HmacValidator.validate` passes.

### Proof of Concept
1. Install the app on `attacker-shop.myshopify.com`; capture a real inbound webhook request: raw body `B` and header `x-shopify-hmac-sha256: H` (valid because `H = HMAC(secret, B)`).
2. Send a new HTTP request to the app's webhook endpoint with the identical raw body `B` and header `x-shopify-hmac-sha256: H`, but set `x-shopify-shop-domain: victim-shop.myshopify.com` instead of the attacker's own shop domain.
3. `ShopifyAPI::Webhooks::Registry.process` (`lib/shopify_api/webhooks/registry.rb:188-200`) calls `Utils::HmacValidator.validate(request)`, which passes because it only checks `HMAC(secret, B) == H`.
4. The handler receives `WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", body: <attacker-controlled B>, ...)`, i.e., attacker-controlled data attributed to a victim tenant.

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
