### Title
Webhook `shop-domain` header is trusted without being covered by the HMAC signature, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` validates a webhook solely by checking the HMAC of the raw request body, but the `shop` (and `topic`/`webhook_id`) values that are subsequently trusted and handed to the application's webhook handler come from HTTP headers that are **not** included in the signed data at all.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw body: [1](#0-0) 

while `shop`, `topic`, `api_version`, and `webhook_id` are all read straight from HTTP headers without any cryptographic binding to the signed payload: [2](#0-1) 

`Registry.process` validates the HMAC using the gem's single, app-wide `Context.api_secret_key` (the same secret is used regardless of which merchant's shop is claimed in the header) and then immediately trusts `request.shop` to build the metadata delivered to the handler: [3](#0-2) [4](#0-3) 

The intended identity binding is: *the shop whose data produced this HMAC-authenticated body == the shop attributed to the webhook event*. Because the app's secret is the same for every installed shop and the shop-domain header sits entirely outside the signed bytes, that equality does not hold. Anyone who can obtain one validly-signed webhook body/HMAC pair for the app (e.g., by installing the app on their own store, which is possible for any public/unlisted Shopify app, and capturing a webhook Shopify sends them) can replay that exact body+HMAC to the app's webhook endpoint while substituting an arbitrary `shopify-shop-domain` header value. `HmacValidator.validate` will still return `true` because it only recomputes the signature over `@raw_body`, and `Registry.process` will hand the forged shop identity to the handler as if it were authentic.

### Impact Explanation
Any webhook handler that uses `WebhookMetadata#shop` to look up or mutate per-tenant state (the documented, expected usage pattern for this gem, e.g., processing `app/uninstalled`, GDPR, or order/customer webhooks) can be made to act on the wrong merchant's data using an attacker-controlled shop domain string, with a body the attacker fully controls (since they generated it via their own legitimate installation). This is a cross-tenant data-integrity/access issue: the app processes an event "from shop B" that was actually authored and signed under shop A's delivery, using content of the attacker's choosing.

### Likelihood Explanation
Requires only an internet-reachable webhook endpoint and the ability to install the app once (or otherwise obtain one valid signed payload), which is realistic for any publicly listed or dev-store-installable Shopify app; no privileged credentials, access tokens, or `client_secret` are needed by the attacker.

### Recommendation
Bind the shop identity into the signed material, or otherwise independently authenticate the shop the header claims: e.g., include the `shop-domain` (and `topic`) header values in `to_signable_string`, or look up the target shop's own stored access-token/secret context and reject webhooks whose header-claimed shop does not match records already known to the app for that delivery (Shopify's own delivery guarantees a matching shop, but this gem's `Request`/`Registry` should not silently assume the header is trustworthy for identity purposes without cryptographic coverage).

### Proof of Concept
1. Install the target app on an attacker-controlled Shopify development store; capture a legitimate webhook delivery `POST` (raw body + `X-Shopify-Hmac-Sha256` + other headers).
2. Verify `HmacValidator.validate` accepts the body unmodified — confirmed by `compute_signature(verifiable_query.to_signable_string, secret)` only hashing `@raw_body` (`lib/shopify_api/utils/hmac_validator.rb:26-31`, `lib/shopify_api/webhooks/request.rb:35-38`).
3. Replay the exact same raw body and HMAC to the target app's webhook endpoint, but change `X-Shopify-Shop-Domain` to a victim shop's domain.
4. `ShopifyAPI::Webhooks::Registry.process` still validates the HMAC successfully (`lib/shopify_api/webhooks/registry.rb:190`) and dispatches the handler with `shop: request.shop` set to the victim domain (`lib/shopify_api/webhooks/registry.rb:198-199`), letting the attacker-crafted body be processed under the victim shop's identity.

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
