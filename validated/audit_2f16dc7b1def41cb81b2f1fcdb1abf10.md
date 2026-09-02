### Title
Webhook shop identity is not bound by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` validates an incoming webhook using only an HMAC over the raw request body, then trusts the unauthenticated `x-shopify-shop-domain` header as the shop identity passed to the app's handler. Because the shop is not part of the signed payload, a valid `(body, hmac)` pair obtained from one shop's webhook delivery can be replayed with a different `shop-domain` header, causing the app to process the webhook as belonging to a different (victim) shop while the HMAC check still passes.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` only returns `@raw_body`: [1](#0-0) 

The `shop`, `topic`, `webhook_id`, and `api_version` are all parsed from HTTP headers that are never included in the signable string: [2](#0-1) 

`Utils::HmacValidator.validate` computes the HMAC only over `verifiable_query.to_signable_string`, i.e. the raw body: [3](#0-2) 

`Registry.process` performs the HMAC check and then immediately trusts `request.shop` (and `request.topic`, `request.webhook_id`) to build the `WebhookMetadata` dispatched to the app's handler: [4](#0-3) [5](#0-4) 

This is a genuine gap in this gem's own binding logic, not a host-application misuse: the same shared `api_secret_key` HMAC-signs the body identically for every shop that installs the app, so the signature carries no shop-specific binding. Contrast this with the OAuth callback verification (`AuthQuery#to_signable_string`), where `shop` IS explicitly part of the signed content: [6](#0-5) 

The equality that should hold is: **shop asserted by the verified signature == shop the handler acts upon**. In the webhook path, the verified quantity is only `HMAC(body, api_secret_key)`; the shop the handler acts upon is an unauthenticated header value. These are two independent quantities, so the binding is broken: `hmac_valid(body) ⇏ shop_header_is_authentic`.

### Impact Explanation
Any actor who can install the vulnerable app on a shop they control (a normal, unprivileged action, not requiring `api_secret_key` or any Shopify-issued credential) can capture a legitimately-signed `(raw_body, hmac)` pair for their own store's webhook delivery (e.g. via their own logging/proxy in front of their webhook endpoint, which they control since it's their own app instance/test environment). They can then replay that exact `(raw_body, hmac)` to the target app's webhook endpoint while substituting the `x-shopify-shop-domain` header with a victim shop that also has the app installed. Because HMAC verification never inspects the shop header, `Registry.process` will accept the forged request as valid and hand the handler a `WebhookMetadata` whose `shop` field names the victim, not the actual originator. Any handler that keys per-shop state off `data.shop` (e.g. `app/uninstalled` cleanup, billing state changes, order/customer data writes) will act on the victim shop's records using attacker-supplied body content — a cross-tenant integrity/confidentiality violation across the app's merchant base.

### Likelihood Explanation
Exploitation requires no privileged credentials, tokens, or `api_secret_key` knowledge — only the ability to install the target app on any shop (which is the normal, unauthenticated first step every merchant/attacker takes) and to observe one webhook delivery's `(body, hmac)` pair from that installation. Replaying it against the shared endpoint with a modified header is trivial once that pair is obtained. The only friction is capturing a valid `(body, hmac)` sample, which is fully within reach of a self-installing attacker controlling their own webhook endpoint infrastructure.

### Recommendation
Bind the shop (and ideally topic/webhook id) into the value that is HMAC-verified, or otherwise cryptographically tie the header-derived shop to the signed payload before it is trusted by `Registry.process`/`WebhookHandler` implementations — for example by including the `shop-domain` header in `to_signable_string`, matching the pattern already used in `Auth::Oauth::AuthQuery`. At minimum, document and enforce that consumers must cross-check `WebhookMetadata#shop` against an independently known/authorized shop record (e.g. the shop tied to the session/webhook subscription id) before performing any tenant-scoped action.

### Proof of Concept
1. Install the target app on attacker-controlled shop `attacker.myshopify.com`; capture one legitimate webhook delivery, e.g. `app/uninstalled`, giving `raw_body = B` and header `x-shopify-hmac-sha256 = H` (valid because `H = HMAC_SHA256(api_secret_key, B)`).
2. Craft a new HTTP request to the same app's webhook endpoint with:
   - `raw_body = B` (unchanged)
   - `x-shopify-hmac-sha256 = H` (unchanged)
   - `x-shopify-topic = app/uninstalled` (unchanged)
   - `x-shopify-shop-domain = victim.myshopify.com` (changed)
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks `HMAC_SHA256(api_secret_key, B) == H`, per `lib/shopify_api/utils/hmac_validator.rb#L26-31` and `lib/shopify_api/webhooks/request.rb#L35-38`.
4. The handler receives `WebhookMetadata.new(shop: "victim.myshopify.com", topic: "app/uninstalled", body: parsed(B), ...)` per `lib/shopify_api/webhooks/registry.rb#L198-199`, and any app logic keyed on `data.shop` (e.g., revoking access, deleting stored data, triggering billing changes) executes against the victim tenant using attacker-controlled content — despite the victim never having sent this event.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
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

**File:** lib/shopify_api/webhooks/webhook_handler.rb (L6-12)
```ruby
    class WebhookMetadata < T::Struct
      const :topic, String
      const :shop, String
      const :body, T::Hash[String, T.untyped]
      const :api_version, String
      const :webhook_id, String
    end
```

**File:** lib/shopify_api/auth/oauth/auth_query.rb (L33-43)
```ruby
        sig { override.returns(String) }
        def to_signable_string
          params = {
            code: code,
            host: host,
            shop: shop,
            state: state,
            timestamp: timestamp,
          }
          URI.encode_www_form(params)
        end
```
