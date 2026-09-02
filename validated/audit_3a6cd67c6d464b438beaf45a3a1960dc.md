### Title
Webhook `shop` identity field is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC only over the raw request body, but the gem trusts the unauthenticated `shopify-shop-domain` header as the tenant identity passed to the app's webhook handler. This breaks the binding `shop authenticated == shop the handler acts on`, matching the report's bug-class hint of "a field acted on but not covered by the HMAC."

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop` is read directly from the `shopify-shop-domain`/`x-shopify-shop-domain` header, with no cryptographic binding to the HMAC or the body: [2](#0-1) 

`Registry.process` validates only the HMAC-over-body via `HmacValidator.validate`, then immediately trusts `request.shop` and forwards it to the app's handler as tenant identity: [3](#0-2) 

`HmacValidator.validate_signature` confirms the signature is computed strictly over `to_signable_string` (the body), never the headers: [4](#0-3) 

The `WebhookMetadata` struct that reaches the app-level handler carries this unauthenticated `shop` field as if it were verified: [5](#0-4) 

The gem's own documentation instructs integrators to use `data.shop` directly to key per-tenant work (e.g. `perform_later(topic: data.topic, shop_domain: data.shop, ...)`), reinforcing that this field is treated as the authenticated tenant identity by design: [6](#0-5) 

**Identity binding broken (equality that should hold but doesn't):**
`shop domain the HMAC was computed for == shop domain value delivered to the handler`

Before attacker action: a genuine Shopify webhook for shop A arrives with body B, `hmac = HMAC(secret, B)`, and header `shop-domain: A`. `HmacValidator.validate` succeeds because it only checks `HMAC(secret, B) == received_hmac`; it never checks that `A` is the shop the message was actually generated for (nothing in the payload ties `A` to `B` cryptographically from the gem's perspective — the gem doesn't reconstruct the signable string using the header value).

Attacker action: an unprivileged internet user replays the exact same `raw_body` and `hmac-sha256` header (both are visible to anyone who can observe or receive a Shopify webhook delivery, e.g. as the operator of a second, attacker-owned shop that legitimately receives webhooks with a body of their choosing/knowledge, such as an app-uninstalled or product webhook whose body content the attacker fully controls or already knows), but sets `shopify-shop-domain` to a victim shop's domain B when POSTing to the app's webhook endpoint.

After attacker action: `HmacValidator.validate` still returns true (body+hmac pair is unchanged and valid), so `Registry.process` proceeds and calls `handler.handle` with `WebhookMetadata.new(shop: "B", body: <attacker-influenced body B>, ...)`. The host application, following the gem's documented pattern, uses `data.shop` to select which merchant's session/tenant context to act on (e.g., look up shop B's access token, mark shop B uninstalled on an `app/uninstalled` topic, apply the body's data to shop B's records) — this is cross-tenant action driven entirely by an attacker-controlled, unauthenticated header.

### Impact Explanation
This crosses the tenant boundary: an attacker who controls (or can predict) one valid `(body, hmac)` pair can cause the host application to process that webhook payload under the identity of an arbitrary other shop domain, since the gem passes an unauthenticated `shop` value on to the handler as if it were verified. Depending on how the host handler uses `data.shop` (which the gem's own docs recommend using directly), this can result in cross-tenant data corruption, spurious uninstall/deauthorization processing for a victim shop, or other tenant-confusion effects — matching the "cross-tenant access" impact category.

### Likelihood Explanation
Exploitability depends on the attacker being able to obtain at least one valid `(raw_body, hmac)` pair — which is trivial for topics where the attacker controls the body content (e.g., their own shop's webhooks, since HMAC uses the same `api_secret_key` for every shop on a given app) and then simply changes the `shop-domain` header when replaying the request to the app's webhook endpoint. No `client_secret`, access token, or privileged access is required — only the ability to send an HTTP POST to the app's public webhook route, and (for the strongest exploitation) legitimate use of the app on the attacker's own shop to harvest a valid signed body.

### Recommendation
Bind the shop identity into the verified signable material, or otherwise validate that the `shop-domain` header corresponds to the actual origin the HMAC covers — e.g., by having the app compare `request.shop` against the shop associated with the session that installed the webhook subscription (rather than trusting the header verbatim), or by having Shopify's webhook payload's own body-embedded shop identifier (if present per topic) be the source of truth instead of the header. At minimum, the gem's documentation should clearly warn that `data.shop` is not covered by the HMAC and must not be trusted as an authenticated value without additional application-side verification against known installed shops.

### Proof of Concept
1. Install the app on attacker-controlled shop A; trigger any webhook topic whose body content the attacker controls or can fully predict (e.g. a metafield/product webhook where attacker sets the body content), capturing the resulting `raw_body` and `x-shopify-hmac-sha256` header — both are valid under the app's single global `api_secret_key`.
2. POST to the app's webhook endpoint with the same `raw_body` and `x-shopify-hmac-sha256`, but replace `x-shopify-shop-domain` with victim shop B's domain, using code equivalent to:
```ruby
ShopifyAPI::Webhooks::Registry.process(
  ShopifyAPI::Webhooks::Request.new(raw_body: captured_body, headers: {
    "x-shopify-topic" => captured_topic,
    "x-shopify-hmac-sha256" => captured_hmac,
    "x-shopify-shop-domain" => "victim-shop.myshopify.com", # attacker-controlled
  })
)
```
3. `HmacValidator.validate` (`lib/shopify_api/utils/hmac_validator.rb:13-22`) returns `true` because it only checks `HMAC(secret, raw_body)`, ignoring the `shop-domain` header; `Registry.process` (`lib/shopify_api/webhooks/registry.rb:188-199`) calls the app handler with `WebhookMetadata(shop: "victim-shop.myshopify.com", body: captured_body, ...)`, causing the host app to process the attacker's chosen webhook body under the victim's tenant identity.

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

**File:** docs/usage/webhooks.md (L24-27)
```markdown
    def handle(data:)
      puts "Received webhook! topic: #{data.topic} shop: #{data.shop} body: #{data.body} webhook_id: #{data.webhook_id} api_version: #{data.api_version}"
      perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)
    end
```
