## Title
Webhook shop/topic identity spoofing via unauthenticated headers not covered by HMAC - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable string from the raw request body only, while the `shop`, `topic`, `webhook_id`, and `api_version` fields that `ShopifyAPI::Webhooks::Registry.process` hands to the app's webhook handler come straight from unauthenticated HTTP headers. The HMAC therefore binds only `body_verified == body_received`; it does nothing to bind `shop_verified == shop_used_by_handler`. Any party who can obtain one valid `(raw_body, hmac)` pair signed with the app's `client_secret` (e.g. a merchant who installs the app on their own store and receives a legitimately signed webhook) can replay that exact body/HMAC pair while forging the `shop-domain` (and `topic`/`webhook-id`) headers to claim the payload originated from a different, victim shop.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

Meanwhile `shop`, `topic`, `webhook_id`, and `api_version` are all read straight from HTTP headers, none of which are part of the signed data: [2](#0-1) 

`HmacValidator.validate` only checks the body against the HMAC secret; it never touches `shop`, `topic`, or `webhook_id`: [3](#0-2) 

`Registry.process` validates the HMAC and then unconditionally forwards the unauthenticated header values (`request.topic`, `request.shop`, `request.webhook_id`, `request.api_version`) to the handler as the identity of the webhook, alongside the (HMAC-verified) body: [4](#0-3) 

Because a single app's `client_secret` is shared across every shop that installs the app, any merchant who installs the app receives legitimately-signed `(raw_body, hmac)` pairs for their own store. Since `hmac` only signs `raw_body`, that exact `(raw_body, hmac)` pair remains valid no matter what `shop-domain`/`topic`/`webhook-id` headers accompany it. An attacker can therefore POST the captured body+HMAC to the app's webhook endpoint with the `shop-domain` header rewritten to a victim shop's domain, and `Registry.process` will accept it as HMAC-valid and hand the handler `WebhookMetadata` claiming the data belongs to the victim shop.

### Impact Explanation
Any app that relies on this gem's documented `WebhookMetadata#shop` (populated from `request.shop`) to determine which tenant/shop a webhook event belongs to — which is exactly how the gem is designed to be used, since it is the only shop identifier surfaced to the handler — can be made to process attacker-controlled data under a victim shop's identity. This breaks the tenant boundary the HMAC is supposed to enforce (`shop_verified == shop_acted_on` does not hold), constituting cross-tenant data injection/confusion using only a webhook subscription the attacker legitimately owns for their own store.

### Likelihood Explanation
Any merchant who installs the public app (a normal, unprivileged action) automatically receives valid `(body, hmac)` pairs signed with the app's shared `client_secret` for ordinary events (e.g., `orders/create`), giving them everything needed to forge headers for a different shop. No access token, secret, or privileged access is required beyond installing the app once as a legitimate low-privilege tenant.

### Recommendation
Bind `shop`, `topic`, and `webhook_id` into the HMAC-signable string (or otherwise cryptographically bind them to the body/signature), so that forging any of these header values invalidates the HMAC. At minimum, `Request#to_signable_string` should incorporate the `shop-domain` header (and ideally `topic`/`webhook-id`) rather than relying solely on the raw body.

### Proof of Concept
1. Attacker installs the target Shopify app on `attacker-shop.myshopify.com`, triggers `orders/create`, and captures the legitimate webhook request: headers `x-shopify-shop-domain: attacker-shop.myshopify.com`, `x-shopify-topic: orders/create`, `x-shopify-hmac-sha256: <valid HMAC over raw_body>`, plus `raw_body`.
2. Attacker replays the exact same `raw_body` and `x-shopify-hmac-sha256` to the app's webhook endpoint, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only verifies `raw_body` against the HMAC: [5](#0-4) 
4. The handler receives `WebhookMetadata` with `shop: "victim-shop.myshopify.com"` and the attacker-controlled `body`, and processes/stores it as if it were genuine data belonging to the victim shop.

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
