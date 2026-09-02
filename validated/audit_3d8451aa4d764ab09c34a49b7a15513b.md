### Title
Webhook `shop`, `topic`, `webhook_id`, and `api_version` are not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signature only over the raw request body, while `shop`, `topic`, `webhook_id`, and `api_version` are read directly from unauthenticated HTTP headers. `Registry.process` validates only the body's HMAC and then dispatches the handler using these unauthenticated header values, so an attacker who possesses one valid `(body, hmac)` pair signed with the app's shared `client_secret` can replay it with a forged `shop-domain`/`topic`/`webhook_id` header and have the app process it as if it came from a different shop.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

Meanwhile `shop`, `topic`, `webhook_id`, and `api_version` are pulled straight from headers with no cryptographic binding to the signature: [2](#0-1) 

`Registry.process` validates the HMAC over the body only, then immediately trusts `request.shop` and `request.topic` (unauthenticated) to build the dispatched metadata: [3](#0-2) 

`HmacValidator.validate` confirms `HMAC(secret, raw_body) == received_signature`, but never checks `HMAC(secret, raw_body) == HMAC(secret, raw_body_bound_to_this_shop_header)`: [4](#0-3) 

The broken identity binding is:
`verified_bytes (raw_body signed by client_secret) == claimed_shop_header (request.shop)` — this equality is never enforced. The gem only verifies `HMAC(secret, body)`, then trusts `shop`/`topic`/`webhook_id` headers unconditionally, even though these fields are what the host application uses to route/attribute the webhook to a tenant.

Because a single app's `client_secret` is shared across every shop that installs the app, any merchant who installs the app can trigger a legitimate webhook delivery to themselves, capture the `(raw_body, hmac)` pair (both of which use the same shared secret and are visible to that merchant, e.g., via their own endpoint logs), and then replay that exact body+signature to the app's webhook endpoint while substituting the `shopify-shop-domain` (and `shopify-topic`/`shopify-webhook-id`) header to any other shop/topic of their choosing. The signature remains valid because it never covered those headers, so `Registry.process` will hand the handler a `WebhookMetadata` claiming to be from the victim shop.

### Impact Explanation
This crosses a tenant boundary: it allows one merchant/installer of an app to make the host application believe attacker-controlled webhook data originated from a different shop. Any host application logic keyed off `WebhookMetadata#shop` (e.g., updating per-shop records, provisioning, billing state, or access decisions) can be manipulated cross-tenant using only a legitimately-received webhook from the attacker's own store — no access token, no leaked credential, and no privileged account needed beyond installing the app on a shop the attacker controls.

### Likelihood Explanation
Likelihood is high for any app relying on this gem's webhook processing: the attacker only needs to be a normal merchant who has installed the target app (a standard, unprivileged action), capture one webhook delivery to their own shop, and replay it with modified headers to the app's public webhook endpoint. No secret material beyond what a normal installer already has access to (their own valid webhook deliveries) is required.

### Recommendation
Bind the routing-relevant fields (`shop`, `topic`, `webhook_id`, `api_version`) into the signed payload verification, e.g. by including them in `to_signable_string` (matching whatever canonicalization Shopify actually signs, if these fields are truly part of the signed payload) or, at minimum, cross-checking the header-derived `shop` against a shop value that is itself cryptographically verifiable (e.g., cross-referencing against the currently registered webhook subscription for that `webhook_id`/topic pair via the Admin API before trusting `request.shop`). Reject requests where such trusted binding cannot be established.

### Proof of Concept
1. App `MyApp` is installed on both the attacker's shop `attacker.myshopify.com` and the victim's shop `victim.myshopify.com`, sharing the same `client_secret`.
2. Attacker triggers an event on their own shop (e.g., updates a product) causing Shopify to deliver a webhook to `MyApp`'s endpoint with body `B` and header `X-Shopify-Hmac-Sha256: HMAC(secret, B)`.
3. Attacker captures `(B, HMAC(secret, B))` (e.g., from their own server logs/proxy, since it's delivered to their own installed app instance) and replays it directly to the same endpoint, but sets `X-Shopify-Shop-Domain: victim.myshopify.com` and/or a different `X-Shopify-Topic`.
4. `ShopifyAPI::Webhooks::Request.new` builds a `Request` from these headers/body; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which only checks `HMAC(secret, B)` against the signature — this passes because the body wasn't modified.
5. `Registry.process` dispatches `handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: "victim.myshopify.com", body: parsed_body, ...))`, so the host application processes attacker-controlled data under `victim.myshopify.com`'s identity. [3](#0-2) [5](#0-4)

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-33)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
