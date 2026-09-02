Investigation confirms a genuine analog. The bug-class from the report ("a check that is supposed to gate a critical transition, but the value it's supposed to bind isn't actually covered by that check") maps to this gem's webhook HMAC validation, where the identity fields used downstream (`shop`, `topic`, `webhook_id`) are never part of the signed material.

### Title
Webhook shop/topic identity spoofing via HMAC that only covers the request body - ([File: lib/shopify_api/webhooks/request.rb](lib/shopify_api/webhooks/request.rb))

### Summary
`ShopifyAPI::Webhooks::Registry.process` treats a valid HMAC as proof that the entire webhook request (including which shop and topic it belongs to) is authentic. In reality, the HMAC only covers the raw body; the `shop`, `topic`, and `webhook_id` values that are handed to the app's handler come from unauthenticated HTTP headers.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0)  while `shop`, `topic`, `api_version`, and `webhook_id` are read straight from HTTP headers with no cryptographic binding: [2](#0-1) 

`Utils::HmacValidator.validate` computes the signature purely from `verifiable_query.to_signable_string` (the body) and the app's `api_secret_key`: [3](#0-2) 

`Registry.process` accepts the request once that body HMAC checks out, then dispatches the handler using the header-derived `shop`/`topic`/`webhook_id`, which were never covered by the signature: [4](#0-3) 

The equality the code effectively (and incorrectly) assumes is:
`shop used to authenticate the payload (implicitly, via api_secret_key ownership)` == `shop reported in the x-shopify-shop-domain header and passed to the handler`

These are not the same thing. The `api_secret_key` is shared across every shop that installs the app (it's an app-level secret, not per-shop), so any merchant who installs the app can receive a legitimately-signed webhook for their own shop. Because the signature never covers the shop/topic headers, that exact `body + hmac` pair remains valid if replayed against the app's webhook endpoint with a different `x-shopify-shop-domain` (and/or `x-shopify-topic`, `x-shopify-webhook-id`) header pointing at a victim shop that also uses the same app.

### Impact Explanation
This breaks the tenant-identity binding the HMAC is supposed to provide: the app's webhook handler (which typically looks up the victim's stored session/state by `data.shop` and processes `data.body` as if it originated from that shop) can be made to process attacker-supplied data under another shop's identity — a cross-tenant data-injection/confusion vector. Depending on how the host app uses `webhook_id`/`topic`/`shop` (e.g., to route to per-shop resources, dedupe, or trigger side effects such as data sync or mandatory-webhook compliance actions like GDPR redaction), an attacker can inject spoofed events for a shop they do not control.

### Likelihood Explanation
Requires only unprivileged actions: install the target app on any store, capture one legitimate webhook delivery (body + `x-shopify-hmac-sha256`), and replay it directly to the app's public webhook endpoint with modified `x-shopify-shop-domain`/`x-shopify-topic` headers. No possession of `api_secret_key`, access tokens, or the victim's credentials is needed.

### Recommendation
Bind the shop/topic/webhook-id identity into the value that is verified — e.g., include the relevant headers in the signable string, or require and check the header values against a value derived from a shop-specific secret/session rather than trusting unauthenticated headers for routing decisions with tenant-affecting side effects.

### Proof of Concept
1. Install the vulnerable app on `attacker-shop.myshopify.com`; wait for Shopify to deliver any subscribed webhook (e.g., `orders/create`) — capture the raw body `B` and header `x-shopify-hmac-sha256: H` (`H = HMAC-SHA256(api_secret_key, B)`).
2. Send a raw HTTP POST directly to the app's webhook endpoint with body `B`, `x-shopify-hmac-sha256: H` (unchanged, still valid since it only signs `B`), but set `x-shopify-shop-domain: victim-shop.myshopify.com` (a different store that also has the app installed) and, if desired, a different `x-shopify-topic`/`x-shopify-webhook-id`.
3. `HmacValidator.validate` succeeds because it only checks `B` against `H` using the shared `api_secret_key`: [5](#0-4) 
4. The registered handler is invoked with `shop: "victim-shop.myshopify.com"` and the attacker's chosen body, even though that data never came from `victim-shop`.

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
