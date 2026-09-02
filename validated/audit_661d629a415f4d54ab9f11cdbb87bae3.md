### Title
Webhook `shop-domain` and `topic` Headers Are Not Covered by the HMAC Signature, Enabling Cross-Shop Replay - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its signable string solely from the raw request body, while the `shop`, `topic`, `webhook_id`, and `api_version` values are taken from unauthenticated HTTP headers. `ShopifyAPI::Webhooks::Registry.process` accepts the webhook once the HMAC over the body validates, then dispatches the handler using the header-derived `shop` value without any cryptographic binding between that value and the signed content. An unprivileged internet user who possesses one legitimate (body, HMAC) pair — trivially obtainable by installing the host app on their own shop and receiving a real webhook — can replay that exact body/HMAC pair while substituting the `shopify-shop-domain` (and/or `shopify-topic`) header, causing the host application to process attacker-supplied payload data as belonging to a different, victim shop.

### Finding Description
The relevant binding that should hold is:

`shop_identity_used_by_handler == shop_identity_authenticated_by_HMAC`

In this gem, that equality is broken:

- `to_signable_string` for a webhook request returns only the raw body: [1](#0-0) 
- `shop`, `topic`, `webhook_id`, and `api_version` are all pulled from HTTP headers that are never included in the signed material: [2](#0-1) 
- `HmacValidator.validate_signature` recomputes the signature over `verifiable_query.to_signable_string` (i.e. the body only) and compares it to the `hmac` header: [3](#0-2) 
- `Registry.process` treats a passing HMAC check as authorization to dispatch the handler using the header-derived `shop`, with no secondary check that the shop belongs to the request that was actually signed: [4](#0-3) 

Because the HMAC only proves "this body was signed by Shopify's secret at some point, for some shop," and not "this body belongs to shop X," any holder of one valid `(raw_body, hmac)` pair can pair it with an arbitrary `shopify-shop-domain` header value. `OpenSSL.secure_compare` in the validator will still succeed because the header change does not alter the signed string at all.

### Impact Explanation
This breaks the tenant-isolation boundary the gem is expected to enforce for webhook ingestion: the handler receives a `WebhookMetadata` whose `shop` field is attacker-controlled while its `body`/HMAC came from an unrelated shop's webhook. Any host application that uses `WebhookMetadata#shop` to key persistence, trigger per-shop business logic, or attribute the payload to a merchant record can be made to apply another shop's data under a victim shop's identity, or vice versa — a cross-tenant access/data-confusion condition. This qualifies as Critical (cross-tenant access) per the fixed impact taxonomy for this exercise.

### Likelihood Explanation
Likelihood is high for anyone who can install the host app on their own shop (a normal, unprivileged action for any Shopify merchant/developer) and capture one legitimate webhook body + HMAC pair (e.g. via a test endpoint or network log). No secret key, access token, or privileged account is required — only a public-facing webhook endpoint and one previously observed signed payload, both of which are part of the gem's documented usage pattern.

### Recommendation
Bind the shop identity into the material that is verified, not just trusted from headers:
- Include `shop`, `topic`, and any other headers the application will act on inside `to_signable_string`, if Shopify's signing scheme supports it, or
- Cross-check the header-derived `shop` against an out-of-band verified identity (e.g., look up the webhook subscription by `webhook_id` and confirm the registered shop matches the header) before dispatching the handler in `Registry.process`, and
- Document explicitly for consumers of `WebhookMetadata#shop` that it is not itself authenticated by the HMAC, and that idempotency/webhook_id + shop cross-referencing is required for security-sensitive handlers.

### Proof of Concept
1. Attacker installs the target app on their own shop `attacker.myshopify.com` and lets it emit a real webhook (e.g. `orders/create`). Attacker's own endpoint (or a network capture) records the exact `raw_body` and the `x-shopify-hmac-sha256` header value Shopify sent.
2. Attacker crafts a new HTTP POST to the host app's public webhook endpoint using:
   - the same `raw_body`
   - the same `x-shopify-hmac-sha256` value
   - `x-shopify-shop-domain: victim-shop.myshopify.com` (a shop the attacker does not control)
   - `x-shopify-topic` unchanged or altered to another registered topic
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only verifies `raw_body` against the secret — the `shop-domain` header substitution is invisible to it: [5](#0-4) 
4. The handler is invoked with `WebhookMetadata.new(topic: request.topic, shop: request.shop, body: request.parsed_body, ...)`, where `shop` is `victim-shop.myshopify.com` even though the payload actually originated from `attacker.myshopify.com`'s webhook: [6](#0-5) 
5. Any host-app logic that trusts `data.shop` for record attribution now operates on the victim shop using attacker-controlled payload content.

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
