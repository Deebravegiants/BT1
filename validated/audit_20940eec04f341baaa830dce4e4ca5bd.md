## Title
Webhook HMAC Verification Does Not Bind the `shop-domain`/`topic` Headers to the Signed Body, Enabling Cross-Tenant Webhook Spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` verifies a webhook's HMAC before dispatching it to the registered handler, but the HMAC only ever covers the raw request body. The `shop`, `topic`, `webhook_id`, and `api_version` values that the handler receives (and that a host app uses to attribute the payload to a tenant/shop) come from HTTP headers that are never part of the signed material. This is the same bug class as the BSB22 report: an identity-relevant field (here, the shop that the data is attributed to) is *acted on* by the system but not *bound* by the cryptographic check that is supposed to authenticate the message.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw body: [1](#0-0) 

while `shop`, `topic`, `webhook_id`, and `api_version` are all pulled straight from headers with no cryptographic tie to the body or to each other: [2](#0-1) 

`Registry.process` validates only the body/HMAC pair, and then unconditionally trusts the header-derived `shop`, `topic`, and `webhook_id` fields to build the `WebhookMetadata` passed to the app's handler: [3](#0-2) 

The HMAC computation itself confirms this — it only ever signs `verifiable_query.to_signable_string`: [4](#0-3) 

**Identity binding broken (as an equality):**
`shop_that_produced_valid_hmac(body) == shop_the_handler_is_told_the_data_belongs_to`

This equality is not enforced anywhere. Because the signature is a pure function of `(raw_body, api_secret_key)` and is completely independent of the `shopify-shop-domain` / `shopify-topic` / `shopify-webhook-id` headers, any request carrying a **previously-observed valid `(raw_body, hmac)` pair** will pass `HmacValidator.validate` regardless of which `shop-domain`/`topic`/`webhook-id` headers are attached to it.

### Impact Explanation
An attacker who can install the target app on their own (attacker-controlled) shop — which requires no privileges beyond being an ordinary Shopify merchant/developer, not the app's `client_secret` or any victim credential — will legitimately receive genuine webhook deliveries `(raw_body, hmac)` signed with the app's real secret for their own shop. Because the signature never binds the body to the `shop-domain` header, the attacker can replay that exact `raw_body`/`hmac` pair to the app's public webhook endpoint while substituting a **victim shop's domain** in the `shopify-shop-domain` header (and/or a different `webhook-id`/`topic`). `HmacValidator.validate` still returns `true` (it never inspects those headers), so `Registry.process` invokes the app's handler with `WebhookMetadata` claiming the (attacker-chosen) body belongs to the victim shop. Any host application that uses `WebhookMetadata#shop` to look up the victim's session/store and persist or act on the (attacker-supplied) body content is exposed to cross-tenant data injection — a Critical-class cross-tenant access issue reachable by an ordinary internet user with no access to the app's `client_secret`, access tokens, or victim credentials.

### Likelihood Explanation
Any developer or trial merchant can install a public/embedded Shopify app to legitimately harvest one valid `(raw_body, hmac)` pair for an arbitrary topic they control (e.g. `orders/create` on their own test shop, with body content they largely control by creating the underlying resource). Replaying that captured pair with a swapped `shop-domain` header against the same publicly reachable webhook endpoint requires only basic HTTP tooling — no cryptographic secret, no MITM, and no social engineering.

### Recommendation
Bind the identity-carrying headers into the signed material, or otherwise cryptographically verify that the body/topic/shop tuple is self-consistent, e.g.:
- Include `shopify-shop-domain`, `shopify-topic`, and `shopify-webhook-id` in the value passed to `to_signable_string` before computing/validating the HMAC, so a captured signature cannot be replayed under a different shop or topic; or
- Additionally, cross-check that the shop asserted by the webhook belongs to a session/shop the app actually expects/has installed for that specific webhook subscription (e.g., correlate `webhook_id` against the ID returned when the webhook was registered for that particular shop) before invoking the handler in `lib/shopify_api/webhooks/registry.rb`.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and triggers a genuine webhook (e.g. `orders/create`) whose body they control the content of (order note, line item titles, etc.).
2. Attacker's endpoint (or a captured proxy log they control, since it's their own shop) records the legitimate headers and raw body:
   ```
   POST /webhooks HTTP/1.1
   X-Shopify-Topic: orders/create
   X-Shopify-Hmac-Sha256: <valid-hmac-for-body>
   X-Shopify-Shop-Domain: attacker-shop.myshopify.com
   X-Shopify-Webhook-Id: <id>

   {"id": 1, "note": "<attacker payload>"}
   ```
3. Attacker resends the identical body and `X-Shopify-Hmac-Sha256` value to the same public webhook endpoint of the victim's installation, only changing:
   ```
   X-Shopify-Shop-Domain: victim-shop.myshopify.com
   ```
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which only recomputes the HMAC over `raw_body` — [4](#0-3)  — so validation succeeds despite the domain swap.
5. The handler is invoked with `WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", body: <attacker payload>, ...)` — [5](#0-4)  — causing the host app to process attacker-controlled data under the victim shop's tenant context.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
