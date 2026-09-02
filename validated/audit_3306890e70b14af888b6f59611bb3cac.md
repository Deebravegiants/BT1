This confirms the finding. The gem's own documentation explicitly tells app developers that `Registry.process` "will verify the request did indeed come from Shopify" (`docs/usage/webhooks.md:125`) and presents `data.shop` as the trusted shop domain to key subsequent logic (`shop_domain: data.shop`) on `docs/usage/webhooks.md:26`, while the actual implementation only HMACs the raw body, not the shop domain.

### Title
Webhook `shop` domain is not covered by HMAC verification, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` verifies a webhook by validating the HMAC over the raw request body only, then trusts the `x-shopify-shop-domain` header verbatim as the tenant identifier passed to the app's handler, even though that header is never included in the signed payload.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) , and `HmacValidator.validate_signature` computes/compares the HMAC exclusively over that signable string [2](#0-1) . The `shop`, `topic`, `webhook_id`, and `api_version` values are all read straight from HTTP headers via `shopify_header` [3](#0-2)  and are never part of the signed bytes. `Registry.process` only checks `Utils::HmacValidator.validate(request)` before forwarding `request.shop` straight into `WebhookMetadata` for the app's handler [4](#0-3) .

This breaks the identity binding: `HMAC(body) == valid` should imply `shop == the shop that actually sent this body`, but the gem only proves `HMAC(body)` is valid for *some* body issued under the app's `client_secret` — it says nothing about which header value accompanied it. Any entity capable of triggering a legitimately-signed webhook for their own shop (e.g., a merchant who installs the app, which requires no special privilege) can capture a valid `(raw_body, hmac)` pair and resend it to the app's webhook endpoint with the `x-shopify-shop-domain` header rewritten to a different (victim) shop. The HMAC check still passes because it only validates the body bytes, and the handler receives `WebhookMetadata.shop` claiming the victim's domain while `body` is genuinely attacker-controlled content originally issued for the attacker's own shop.

### Impact Explanation
Applications built on this gem are documented to treat `data.shop` as the authoritative tenant identifier once `Registry.process` "verifies the request did indeed come from Shopify" [5](#0-4) , and to key downstream work off it directly, e.g. `perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)` [6](#0-5) . Because the gem's own verification step never binds `shop` to the signed bytes, an attacker with a legitimate install of the app on their own store can forge webhook deliveries "from" any other shop domain, causing the host application to write/attribute data (orders, inventory changes, etc.) into the wrong tenant's records — a cross-tenant confusion driven purely by this gem's incomplete verification, not by any host misuse.

### Likelihood Explanation
Requires only an unprivileged actor able to install the app (or otherwise trigger a webhook targeting their own controlled endpoint to capture a valid body/HMAC pair) and the ability to POST directly to the target app's public webhook callback URL with a modified header — no access to `api_secret_key`, tokens, or TLS interception is needed.

### Recommendation
Include the header-derived fields (`shop`, `topic`, `webhook_id`, `api_version`) in the signable string used for HMAC computation, or independently cross-check `request.shop` against a shop already known/authorized by the application (e.g. compare against the shop tied to the webhook subscription) before trusting it in `WebhookMetadata`.

### Proof of Concept
1. Install the app on shop `attacker.myshopify.com`; trigger any subscribed webhook topic (e.g. `orders/create`) so Shopify sends a legitimately HMAC-signed POST to the app's registered callback URL.
2. Capture the raw request body and the `x-shopify-hmac-sha256` header value from that delivery (attacker fully controls the endpoint/logging for their own shop).
3. Replay the exact same `raw_body` and `hmac` header to the app's webhook endpoint, but replace `x-shopify-shop-domain` with `victim.myshopify.com`.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which only checks `HMAC(raw_body)` and passes [7](#0-6) ; the handler then receives `WebhookMetadata.new(shop: "victim.myshopify.com", body: <attacker's data>, ...)`, causing the host app to process attacker-controlled data as if it came from the victim shop.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-33)
```ruby
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

**File:** docs/usage/webhooks.md (L24-27)
```markdown
    def handle(data:)
      puts "Received webhook! topic: #{data.topic} shop: #{data.shop} body: #{data.body} webhook_id: #{data.webhook_id} api_version: #{data.api_version}"
      perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)
    end
```

**File:** docs/usage/webhooks.md (L123-126)
```markdown
## Process a Webhook

To process an http webhook, you need to listen on the route(s) you provided during the Webhook registration process, then when the route is hit construct a `ShopifyAPI::Webhooks::Request` and call `ShopifyAPI::Webhooks::Registry.process`. This will verify the request did indeed come from Shopify and then call the specified handler for that webhook. An example in Rails is shown below:

```
