Based on my review of `lib/shopify_api/webhooks/**` and `lib/shopify_api/utils/hmac_validator.rb`, I found a valid analog matching the "field acted on but not covered by the HMAC" bug class.

### Title
Webhook `shop` (and `topic`/`webhook-id`) identity fields are not covered by the HMAC signature, enabling cross-tenant webhook replay - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-verifiable signable content from the raw request body only, while `shop`, `topic`, `webhook_id`, and `api_version` are read directly from unauthenticated HTTP headers and are never included in the HMAC computation. `Webhooks::Registry.process` validates only the body's HMAC and then dispatches the handler using the header-derived `shop`, breaking the intended binding between "the bytes cryptographically verified" and "the shop identity acted upon."

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

Meanwhile `shop`, `topic`, `webhook_id`, and `api_version` are pulled straight from HTTP headers with no cryptographic binding to the signed payload: [2](#0-1) 

`Registry.process` validates only the HMAC of the body via `Utils::HmacValidator.validate(request)`, then immediately trusts `request.shop` (and other header fields) to build the `WebhookMetadata` passed to the host app's handler: [3](#0-2) 

`HmacValidator.validate` calls `verifiable_query.to_signable_string`, which for a `Webhooks::Request` is just the raw body — the `shop-domain` header plays no role in the signature: [4](#0-3) 

The broken identity binding, stated as an equality that should hold but doesn't:
`shop header value used to attribute the webhook == shop that the HMAC-signed body actually originated from`

Because the `shop-domain` header is not part of the signed content, any party who possesses one valid `(body, hmac)` pair for the app's `client_secret` — e.g., an attacker who installs the app on their own shop and receives a legitimate webhook for it — can replay that exact body+HMAC to the app's webhook endpoint while substituting a different `shop-domain` (and `topic`/`webhook-id`) header value. `HmacValidator.validate` still returns `true` because it only checks the body bytes, and `Registry.process` forwards the attacker-chosen `shop` to the handler as if it were authentic.

### Impact Explanation
Host applications built on this gem are documented to trust `WebhookMetadata#shop` for tenant attribution once `Registry.process` returns without error (i.e., once HMAC validation "passes"). Since the shop field is unauthenticated, an attacker controlling one legitimate webhook delivery (from their own store) can forge deliveries that are misattributed to an arbitrary victim shop domain, causing cross-tenant data corruption/confusion in the host application (e.g., an attacker's order/webhook payload being processed as belonging to another merchant's shop). This falls under "cross-tenant access" impact.

### Likelihood Explanation
Exploitation requires the attacker to install the app on their own store (a normal, unprivileged action for any Shopify merchant) and capture one webhook delivery, then replay the raw body+HMAC to the same public webhook endpoint with a spoofed `shop-domain` header value naming a victim shop. No access token, secret, or privileged account is required — only observation of one's own legitimately received webhook.

### Recommendation
Include the identity-bearing headers (`shop-domain`, `topic`, `webhook-id`, `api-version`) in the HMAC-signed content, or otherwise cryptographically bind them to the verified payload, so that `HmacValidator.validate` fails if any of these fields are altered independently of the signed body. At minimum, document prominently that `request.shop`/`request.topic` are unauthenticated and must not be trusted for tenant attribution without additional verification (e.g., cross-checking against the shop associated with the resource ID in the payload).

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and triggers a webhook (e.g., `orders/create`) that Shopify delivers with a valid `x-shopify-hmac-sha256` for that raw body.
2. Attacker replays the exact same raw body and HMAC header to the app's webhook endpoint, but changes `x-shopify-shop-domain` to `victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which only hashes `@raw_body` — validation succeeds.
4. The handler receives `WebhookMetadata` with `shop: "victim-shop.myshopify.com"` even though the payload never touched that shop, and the host application processes/stores data under the wrong tenant.

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
