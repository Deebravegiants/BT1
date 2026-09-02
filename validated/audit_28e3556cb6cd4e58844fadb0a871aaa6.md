### Title
Webhook shop/topic/version identity fields are not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` binds HMAC validation to the raw request body only, while the `shop`, `topic`, `api_version`, and `webhook_id` values that the host application uses to attribute the webhook to a specific tenant are taken from unauthenticated HTTP headers. Anyone who can obtain one validly-signed webhook body/HMAC pair for the app (e.g., by installing the app on their own store, which requires no special privilege) can replay that body with a forged `shop-domain` header pointing at a different, victim shop, and `HmacValidator.validate` will still report the signature as valid.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop`, `topic`, `api_version`, and `webhook_id` are read straight from HTTP headers, which are not part of the signed material: [2](#0-1) 

`Registry.process` validates only `Utils::HmacValidator.validate(request)` — i.e., it checks `hmac == HMAC(raw_body, client_secret)` — and then immediately forwards `request.shop` (an unverified header) into `WebhookMetadata` that is handed to the host application's handler: [3](#0-2) 

`HmacValidator.validate_signature` computes and compares the signature purely against `verifiable_query.to_signable_string`, i.e., the body bytes, with no binding to shop/topic/version: [4](#0-3) 

This is the exact "bytes verified versus bytes parsed" identity-binding break named in the analysis rules: the gem verifies only the body bytes but the identity-critical field (`shop`) is parsed from unauthenticated headers and passed on as authenticated (`WebhookMetadata#shop`): [5](#0-4) 

Because the same `client_secret` signs webhook bodies for every shop that installs the app (multi-tenant SaaS model), a merchant/attacker who legitimately installs the app on their own store receives real webhook deliveries whose `hmac` is valid for that raw body. Nothing prevents them from replaying that exact `(raw_body, hmac)` pair to the app's webhook endpoint while substituting the `x-shopify-shop-domain` (or `shopify-shop-domain`) header with a victim shop's domain. `HmacValidator.validate` will still accept it because it never looks at the shop header, and `Registry.process` will hand the host app a `WebhookMetadata` claiming the data belongs to the victim shop.

### Impact Explanation
This breaks the tenant identity binding `shop_authenticated == shop_acted_on`: the shop that is cryptographically proven to have produced the bytes (the attacker's own shop, since they hold a valid HMAC for their own webhook body) is not equal to the shop value the host application is told to act on (an arbitrary victim shop domain chosen by the attacker). Any host application that trusts `WebhookMetadata#shop` to route webhook data to per-tenant state (e.g., writing order/customer data into the victim's tenant record, or triggering per-shop side effects) is exposed to cross-tenant data injection/confusion — this matches the Critical "cross-tenant access" impact category, since it lets one tenant's authenticated request bytes be relabeled as belonging to any other tenant.

### Likelihood Explanation
Likelihood is high for any app builder who relies on the gem's provided `request.shop`/`WebhookMetadata#shop` as the source of truth for tenant identity (which is the documented, intended usage pattern of `Webhooks::Registry.process`). The only prerequisite is installing the app on any single shop (a normal, unprivileged, self-service action for any Shopify merchant/developer using the public app), then capturing one webhook delivery to obtain a valid `(raw_body, hmac)` pair, which can then be replayed indefinitely with an arbitrary spoofed `shop-domain` header.

### Recommendation
Include `shop`, `topic`, `api_version`, and `webhook_id` in the signed/verified material, or otherwise cryptographically bind the shop domain to the payload before trusting it — e.g., have `to_signable_string` incorporate the header values that the handler consumes, or independently verify the shop domain against a session/store lookup keyed by a value that is itself covered by the HMAC, rather than trusting header-derived `request.shop` uncritically in `WebhookMetadata`.

### Proof of Concept
1. Attacker installs the Shopify app on their own store `attacker-shop.myshopify.com` and receives a legitimate webhook, e.g., `orders/create` with body `{"id":1}` and header `x-shopify-hmac-sha256: <valid HMAC of body>`.
2. Attacker resends that exact `raw_body` and `hmac` header to the app's webhook endpoint, but changes `x-shopify-shop-domain` to `victim-shop.myshopify.com`.
3. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which only recomputes the HMAC over `raw_body` — unaffected by the header change — and returns `true`.
4. The handler receives `WebhookMetadata.new(shop: "victim-shop.myshopify.com", topic: "orders/create", body: {"id"=>1}, ...)` as if the victim shop generated this webhook, even though the victim never sent it.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
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
