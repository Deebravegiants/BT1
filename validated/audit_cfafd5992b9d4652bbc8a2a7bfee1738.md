### Title
Webhook shop-domain header is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC over the raw request body, while the `shop` identifier that is handed to the application's webhook handler is read from an HTTP header that is never covered by that signature.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`, and the HMAC digest is computed exclusively over the body: [1](#0-0) 

The `shop` (and `topic`, `api_version`, `webhook_id`) values used downstream are pulled from HTTP headers instead: [2](#0-1) 

`Registry.process` validates the request using `Utils::HmacValidator.validate(request)`, which in turn calls `to_signable_string` (body only) and compares it against the computed signature for `Context.api_secret_key`: [3](#0-2) 

After this check passes, `Registry.process` builds the metadata object handed to the app's handler using `request.shop` — the unauthenticated header value: [4](#0-3) 

The identity binding that should hold is: `shop authenticated by HMAC == shop the handler acts on`. Because the signature only binds the body bytes, not the shop header, this equality does not hold. Any two occurrences of an HTTP webhook delivery from Shopify sharing the same `hmac-sha256`/body pair (e.g., a webhook whose payload is empty or identical across deliveries — the mandatory `shop/redact`, `customers/redact`, or `customers/data_request` payloads, or any topic delivered with the same body content to more than one shop, or replay of a single previously-observed delivery to the same endpoint with a substituted `X-Shopify-Shop-Domain`/`X-Shopify-Hmac-Sha256` header pair captured from a shop the attacker controls) will still pass `HmacValidator.validate` and be attributed to whatever `shop` header value accompanies the replayed request.

### Impact Explanation
This breaks the binding between "the request Shopify actually signed for shop A" and "the shop the host application believes the webhook came from and acts on." Since host applications (e.g. via `WebhookMetadata#shop`) commonly use this value as the tenant key to look up merchant records, credentials, or state, a forged/replayed `shop` header lets an attacker who controls their own shop's valid webhook deliveries cause the receiving application to process or attribute webhook data under a victim shop's identity — a cross-tenant access condition.

### Likelihood Explanation
Any Shopify Partner/developer can register an app on their own store and receive genuinely-signed webhook deliveries with attacker-known raw bodies (mandatory compliance topics have fixed/predictable bodies, e.g. `{}`), then simply resend that same body+signature pair to the app's webhook endpoint while modifying only the `X-Shopify-Shop-Domain` header. No secret material or privileged access is required — the attacker uses their own store's legitimately obtained signature.

### Recommendation
Include the `shop`, `topic`, `webhook_id`, and `api_version` header values in the signable string (or otherwise cryptographically bind them, e.g. via a signed JWT/session-token-style claim) so `HmacValidator.validate` fails whenever any of these headers is altered relative to what Shopify actually sent.

### Proof of Concept
1. Register a webhook handler in the host app relying on `data.shop` from `WebhookMetadata`.
2. Obtain (or predict) a valid `{raw_body, X-Shopify-Hmac-Sha256}` pair — e.g. from the mandatory `shop/redact` webhook fired to the attacker's own store, whose body is deterministic JSON.
3. Send an HTTP POST to the app's webhook endpoint reusing that exact body and HMAC header, but set `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks `raw_body` against the secret — `lib/shopify_api/webhooks/request.rb:35-38` and `lib/shopify_api/utils/hmac_validator.rb:12-22`.
5. The handler is invoked with `WebhookMetadata.new(... shop: request.shop ...)` reporting the victim shop — `lib/shopify_api/webhooks/registry.rb:198-199` — even though Shopify never sent this event for that shop.

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
