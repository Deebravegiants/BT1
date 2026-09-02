### Title
Webhook shop/topic identity not bound by HMAC, allowing cross-tenant webhook spoofing via replay - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`, `lib/shopify_api/utils/hmac_validator.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` only verifies the HMAC over the webhook's raw body, but dispatches the handler using the `shop` and `topic` values taken from unauthenticated HTTP headers that are never included in the signed payload. This mirrors the reported "wrong value covered by verification" bug class: the check (body HMAC) and the value acted upon (shop identity used to route/attribute the webhook) are not the same thing.

### Finding Description
`Utils::HmacValidator.validate` computes the signature strictly from `verifiable_query.to_signable_string` and the app's shared `api_secret_key`: [1](#0-0) 

For webhooks, `to_signable_string` returns only the raw request body — never the shop domain, topic, or webhook id: [2](#0-1) 

Those identity fields (`shop`, `topic`, `webhook_id`, `api_version`) are read straight from HTTP headers that carry no cryptographic binding at all: [3](#0-2) 

`Registry.process` validates only the body HMAC, then immediately builds `WebhookMetadata` using the unauthenticated `request.shop` and `request.topic`, handing this straight to the app's registered handler: [4](#0-3) 

Because `api_secret_key` is a single value shared across all shops installed on the app (not per-shop), a valid `(body, hmac)` pair produced for one shop's webhook remains cryptographically valid no matter what `x-shopify-shop-domain` header accompanies it. The binding that should hold is:
`hmac_valid ⇒ (body, shop, topic) authentic`
but the code only guarantees:
`hmac_valid ⇒ body authentic`

### Impact Explanation
A user who legitimately operates a shop with the app installed can capture one of their own valid webhook deliveries (body + `x-shopify-hmac-sha256`), then replay that exact body/HMAC pair to the app's webhook endpoint while substituting an arbitrary `x-shopify-shop-domain` header for a different, victim tenant. `HmacValidator.validate` still succeeds (it never looked at the header), and `Registry.process` calls the handler with `WebhookMetadata#shop` set to the spoofed victim shop and the attacker-controlled body. Any host application that trusts `WebhookMetadata#shop` to scope data writes, session lookups, or business logic (the gem's own documented `WebhookMetadata` contract) will process attacker-supplied data under another tenant's identity — a cross-tenant access/data-injection primitive, without needing the app's `client_secret`, an access token, or TLS interception.

### Likelihood Explanation
Exploitation only requires the ability to send an HTTP request to the app's public webhook endpoint (which by design accepts unauthenticated internet traffic) plus one previously-received legitimate webhook body/signature pair from any shop that has installed the app — something an ordinary, unprivileged merchant using the app already possesses. No secret material, privileged account, or special network position is required.

### Recommendation
Bind the shop/topic identity into the value that is actually verified: include `shop`, `topic`, and `webhook_id` (in addition to the body) in the signable payload used by `HmacValidator`, or otherwise cryptographically tie the header-derived `shop`/`topic` to the signed body before they are trusted by `Registry.process`/`WebhookMetadata`. At minimum, document that the header-derived `shop` is unauthenticated and must be independently corroborated (e.g., against a known set of shops with an active webhook subscription) by consuming applications before use.

### Proof of Concept
1. App merchant "attacker-shop" installs the app and legitimately receives a webhook, capturing `raw_body` and `x-shopify-hmac-sha256`.
2. Attacker sends a POST to the app's webhook endpoint with the same `raw_body` and `x-shopify-hmac-sha256`, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks the body against the shared `api_secret_key`.
4. The registered handler receives `WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", body: attacker's body, ...)`, and any host logic keyed on `shop` now operates on "victim-shop" using attacker-supplied content.

### Citations

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

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
