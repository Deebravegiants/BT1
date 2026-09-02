### Title
Webhook `shop` (and other Shopify headers) are excluded from HMAC verification, allowing tenant spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signature over the raw request body only, while `shop`, `topic`, `api_version`, and `webhook_id` are read directly from unauthenticated HTTP headers and then handed to the app's webhook handler as trusted, tenant-identifying data. This breaks the intended binding of `hmac ⇒ (body, shop)`; only `hmac ⇒ body` is actually enforced.

### Finding Description
`Request#to_signable_string` returns solely `@raw_body`: [1](#0-0) 

but `Request#shop`, `#topic`, `#api_version`, and `#webhook_id` are pulled straight from HTTP headers with no cryptographic binding to that signature: [2](#0-1) 

`Registry.process` validates only the body's HMAC and then constructs `WebhookMetadata` directly from these unauthenticated header values, passing it to the app's handler as if `shop` were an authenticated field: [3](#0-2) 

`WebhookMetadata` itself declares `shop` as a plain, unqualified `String` field with no indication it is unverified: [4](#0-3) 

The equality this gem is supposed to guarantee to consumers is: `hmac_valid? ⇒ (body, shop) both authentic`. In reality it only guarantees `hmac_valid? ⇒ body authentic`; `shop` (and `topic`/`webhook_id`/`api_version`) can be freely set by anyone who can reach the app's public webhook endpoint, because `HmacValidator.validate` (`lib/shopify_api/utils/hmac_validator.rb:13-22`) only ever sees `to_signable_string`, never the headers.

### Impact Explanation
Since `shop` is the tenant-identifying field of the webhook and is exposed to host applications as though it were authenticated (it flows unmodified from header → `Request#shop` → `WebhookMetadata#shop` → handler), any host application that uses `data.shop` to key session/data-store lookups (a very common and documented pattern, since this is the exact purpose of the field) can be made to process a webhook body under an attacker-chosen shop identity. An unprivileged internet user who can reach the webhook receiving endpoint (a webhook endpoint is by definition internet-reachable and does not require any credential) can replay or send a body whose HMAC they don't need to forge if they can pair it with a header value of their choosing — because the signature never covers the header in the first place. This crosses a tenant boundary the caller believes the gem enforces, matching the "field acted on but not covered by the HMAC" analog class.

### Likelihood Explanation
Any request to the app's public webhook route can carry attacker-controlled `X-Shopify-Shop-Domain` (or `shopify-shop-domain`) headers alongside a body/HMAC pair; no secret, session, or credential is needed to control the header value, only knowledge of the endpoint URL and one valid `(body, hmac)` pair for the app's secret (which is unavoidably shared for all shops using a given app installation and observable by that app's own legitimate webhook traffic). This makes exploitation practical for any actor able to send/replay HTTP requests to the endpoint.

### Recommendation
Include `shop` (and ideally `topic`, `api_version`, `webhook_id`) in the signable string used for HMAC verification, or otherwise cryptographically bind them to the signed payload, so `HmacValidator.validate` fails whenever any of these header-derived, tenant-identifying values has been tampered with. At minimum, document clearly in `WebhookMetadata`/`Request` that only `body` is authenticated and that `shop` must not be trusted for tenant-scoped lookups without additional verification (e.g., cross-checking against a known/registered shop).

### Proof of Concept
1. Attacker obtains any single valid `(raw_body, x-shopify-hmac-sha256)` pair for the target app (e.g., by triggering one real webhook event for their own installed shop, or intercepting a benign one they legitimately receive).
2. Attacker sends `POST /webhooks` with the same `raw_body` and `x-shopify-hmac-sha256`, but sets `x-shopify-shop-domain: victim-shop.myshopify.com` and any desired `x-shopify-topic`.
3. `Utils::HmacValidator.validate` recomputes the HMAC over `to_signable_string` (`@raw_body` only) and it matches, so `Registry.process` proceeds: [5](#0-4) 
4. The handler receives `WebhookMetadata` with `shop == "victim-shop.myshopify.com"` despite the body never having been produced for that shop, allowing cross-tenant action attribution in any host app that keys behavior off `data.shop`.

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
