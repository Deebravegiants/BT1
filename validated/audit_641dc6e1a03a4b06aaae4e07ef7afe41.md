This confirms the documented, expected usage: apps are explicitly told `data.shop` is "The shop domain of the webhook" and the sample handler code passes `data.shop` directly to business logic (`perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)`) as an authoritative tenant identifier. This confirms the finding is exploitable through the gem's own documented API, not by an app "ignoring" it.

### Title
Webhook shop/topic identity spoofing via HMAC that only covers the body, not the `shop-domain`/`topic` headers - ([File: lib/shopify_api/webhooks/registry.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` verifies a webhook only by checking the HMAC of the raw request body [1](#0-0) , then hands `request.shop`, `request.topic`, and `request.webhook_id` — all taken from unauthenticated HTTP headers — straight to the app's handler as trusted identity fields [2](#0-1) . The `to_signable_string` used for HMAC computation is only the raw body [3](#0-2) , so the `shop`, `topic`, and `webhook_id` headers are never bound to the signature [4](#0-3) .

### Finding Description
The identity binding that should hold is: `shop authenticated by HMAC == shop the handler acts on`. In this gem it does not, because:

- `HmacValidator.validate` calls `verifiable_query.to_signable_string`, and for `Webhooks::Request` that string is just `@raw_body` [3](#0-2) .
- `shop`, `topic`, `webhook_id`, and `api_version` are all read from HTTP headers (`shopify-shop-domain`, `shopify-topic`, etc.) that are completely outside the HMAC-signed content [4](#0-3) .
- `Registry.process` only checks `Utils::HmacValidator.validate(request)` (i.e., that the body was signed with the app's `api_secret_key`) and then immediately builds `WebhookMetadata` from the unauthenticated headers and dispatches it to the handler [5](#0-4) .

Because `api_secret_key` is shared by the app across *all* installing shops (it is not per-tenant), any unprivileged merchant who installs the app can trigger a legitimate webhook for their own store and thereby obtain a body + HMAC pair that is validly signed with the app's secret. Nothing prevents that merchant from replaying that exact body/HMAC pair to the app's webhook endpoint while substituting an arbitrary `x-shopify-shop-domain` (and/or `x-shopify-topic`) header value naming a different, victim shop. `Registry.process` will accept it (the HMAC over the body still checks out) and will invoke the handler with `shop: "<victim-shop>.myshopify.com"` while the body content is actually the attacker's own data.

The documentation explicitly instructs app authors to treat `data.shop` as the authoritative tenant identifier for the webhook (`"shop, String - The shop domain of the webhook"`) and shows a canonical handler forwarding it directly into business logic (`perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)`). This is not the app misusing an undocumented API — it is exactly the pattern the gem's own docs recommend, so the gap sits squarely inside the gem's guarantees.

### Impact Explanation
This breaks tenant isolation: an attacker with nothing more than their own (unprivileged) app installation can cause the webhook handler to process attacker-supplied body data under a victim shop's identity. Depending on how the host app uses `data.shop` (as shown in the gem's own documented example — routing persistence/jobs by `shop_domain`), this can lead to cross-tenant data corruption/injection — writing or overwriting a victim shop's records with attacker-controlled content, or bypassing shop-scoped authorization checks that rely on `data.shop`. This matches the Critical "cross-tenant access" impact category.

### Likelihood Explanation
Likelihood is significant for any app that has more than one shop installed (the common case for any public/multi-tenant Shopify app): the attacker needs no privileged access, no leaked secrets, and no TLS interception — only their own store's own webhook delivery (which they can trigger themselves, e.g., by creating an order in their own store) and the ability to send an arbitrary HTTP POST to the app's public webhook endpoint with a modified header.

### Recommendation
Bind the `shop` (and ideally `topic`/`webhook_id`) header values into the HMAC-signed content, or otherwise cryptographically bind them to the verified payload, instead of trusting them as bare headers. At minimum, `VerifiableQuery#to_signable_string` for `Webhooks::Request` should incorporate the `shop-domain` header (and topic) so that `HmacValidator.validate` fails if either has been tampered with relative to what Shopify actually signed. Documentation and the `WebhookMetadata#shop` contract should be updated accordingly once this binding is enforced.

### Proof of Concept
1. Attacker registers/installs the target app on their own store `attacker.myshopify.com` (unprivileged, self-service).
2. Attacker triggers a webhook event on their own store (e.g., creates an order), causing Shopify to POST a body `B` with header `x-shopify-shop-domain: attacker.myshopify.com` and a valid `x-shopify-hmac-sha256` computed over `B` using the app's shared `api_secret_key`.
3. Attacker captures this legitimate `(headers, B)` pair from their own inbox/logs (no interception of anyone else's traffic required).
4. Attacker resends the same `raw_body B` and the same `x-shopify-hmac-sha256` value to the app's webhook endpoint, but replaces the header with `x-shopify-shop-domain: victim.myshopify.com`.
5. `Registry.process` calls `HmacValidator.validate(request)`, which only checks `HMAC(secret, B)` — still valid — then builds `WebhookMetadata.new(shop: "victim.myshopify.com", body: parsed(B), ...)` and invokes the app's handler [5](#0-4) , which (per the gem's documented pattern) acts on `victim.myshopify.com` using attacker-controlled body content.

### Citations

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
