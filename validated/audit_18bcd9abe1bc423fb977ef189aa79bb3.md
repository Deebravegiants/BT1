### Title
Webhook HMAC only covers the request body, not the `shop` domain header, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw HTTP body, while `shop` is read directly from an unauthenticated `x-shopify-shop-domain`/`shopify-shop-domain` header. `Utils::HmacValidator` verifies the HMAC solely over that body-derived signable string, so a valid HMAC only proves "this body was produced with the app's `client_secret_key`" — it proves nothing about which shop the request is attributed to. `Webhooks::Registry.process` still forwards the unauthenticated `request.shop` value straight to the app's handler as the trusted tenant identifier.

### Finding Description
The identity binding the gem is supposed to enforce is: `shop_that_generated_the_hmac == shop_delivered_to_the_handler`. That equality is broken:

- HMAC computation covers only the body: [1](#0-0) 
- `shop` is parsed purely from a header, entirely outside the signed material: [2](#0-1) 
- `HmacValidator.validate` calls `to_signable_string` (body only) as the thing verified against the HMAC secret: [3](#0-2) 
- `Registry.process` validates the HMAC, then immediately passes the unauthenticated `request.shop` into `WebhookMetadata`, which is handed to the app's handler as the trusted shop identity: [4](#0-3) [5](#0-4) 

Because a Shopify app uses a single `client_secret_key` shared across every shop that installs it, any user who can install the app on their own shop can legitimately obtain a body + HMAC pair that Shopify signed for their own store. The HMAC over that body will remain valid no matter what `shop`, `topic`, or `webhook-id` headers accompany it, because those fields are never part of the signed content.

The gem's own documentation confirms host apps are expected to trust the `shop` value coming out of this gem as the tenant key for routing/storage, e.g. `perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)`, and describes `Registry.process` as verifying "the request did indeed come from Shopify": [6](#0-5) [7](#0-6)  That guarantee is false for the `shop` field: it never crosses the HMAC boundary.

### Impact Explanation
An unprivileged internet user who can install the target app on a shop they control (e.g., a free Shopify dev/partner store) can generate a validly-HMAC'd webhook body from their own tenant, then replay it to the app's webhook endpoint with the `shop-domain` header rewritten to a victim's `myshopify.com` domain. `Registry.process` will accept the forged shop attribution as authentic (HMAC check passes) and hand it to the host application's handler, which — per this gem's documented usage pattern — uses `data.shop` as the tenant key to route/store the payload. This is a cross-tenant identity confusion: attacker-controlled body content is durably attributed to a victim shop's tenant context in the consuming application, without any privileged credential, session, or the app's `client_secret`.

### Likelihood Explanation
Exploitation requires only: (1) the ability to install the app on the attacker's own shop (or otherwise trigger a webhook for a shop the attacker controls) to obtain one valid `(body, hmac)` pair, and (2) sending a normal unauthenticated HTTP POST to the app's public webhook endpoint with a modified `shop-domain` header. No secret material, session, or elevated privilege is needed, and the header/body split is baked into how `Request` and `HmacValidator` are implemented, so every consumer of this gem's webhook processing is affected identically.

### Recommendation
Bind `shop` (and ideally `topic`/`webhook-id`) into the value that is HMAC-verified, or otherwise cryptographically tie the header-derived `shop` to the signed body before it is exposed via `WebhookMetadata`. At minimum, `VerifiableQuery#to_signable_string` for webhook `Request` should incorporate the `shop-domain` header (and other identity-bearing headers) so that tampering with them invalidates the HMAC, restoring the equality between "shop that produced a valid signature" and "shop delivered to the handler."

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker-shop.myshopify.com` and triggers a webhook (e.g. `orders/create`), capturing the raw POST: body `B` and header `x-shopify-hmac-sha256: H`, where `H = HMAC-SHA256(client_secret, B)`.
2. Attacker sends a new POST to the app's public webhook endpoint with the same body `B` and same `x-shopify-hmac-sha256: H`, but replaces `x-shopify-shop-domain` with `victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` parses `shop` as `victim-shop.myshopify.com` from the header: [2](#0-1) 
4. `Utils::HmacValidator.validate` recomputes the HMAC over `B` only and it matches `H`, since `shop` was never part of the signed string: [3](#0-2) 
5. `Registry.process` accepts the request and calls the app's handler with `WebhookMetadata.shop == "victim-shop.myshopify.com"`, even though the payload actually originated from the attacker's own shop: [4](#0-3)

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-23)
```ruby
      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
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

**File:** docs/usage/webhooks.md (L24-26)
```markdown
    def handle(data:)
      puts "Received webhook! topic: #{data.topic} shop: #{data.shop} body: #{data.body} webhook_id: #{data.webhook_id} api_version: #{data.api_version}"
      perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)
```

**File:** docs/usage/webhooks.md (L123-125)
```markdown
## Process a Webhook

To process an http webhook, you need to listen on the route(s) you provided during the Webhook registration process, then when the route is hit construct a `ShopifyAPI::Webhooks::Request` and call `ShopifyAPI::Webhooks::Registry.process`. This will verify the request did indeed come from Shopify and then call the specified handler for that webhook. An example in Rails is shown below:
```
