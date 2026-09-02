### Title
Webhook `shop` identity is trusted by handlers but not covered by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` validates only that the *raw body* of an inbound webhook was HMAC-signed with the app's `client_secret`. The `shop`, `topic`, `webhook_id`, and `api_version` values — all taken directly from HTTP headers — are never covered by that signature, yet they are handed to the app's webhook handler as trusted identifiers of which tenant the payload belongs to.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop`, `topic`, `webhook_id`, and `api_version` are read straight from attacker-reachable HTTP headers with no cryptographic binding to the body: [2](#0-1) 

`Registry.process` validates the HMAC using this `to_signable_string` (body only), and then forwards `request.shop` unchanged to the handler as the authoritative tenant identifier: [3](#0-2) 

The `client_secret`/HMAC key is a single **per-app** secret shared across every shop that installs the app — it is not per-shop. This means the equality the gem is implicitly relying on:

`hmac_valid(body, client_secret) == true` ⇒ `shop_header == originating_shop`

does not hold. `hmac_valid` only proves "this body+signature pair was produced by Shopify (or by any shop using this same app) with knowledge of the app's client_secret" — it says nothing about which shop the `shop-domain` header refers to.

### Impact Explanation
Any unprivileged internet user who can install the target app on their own (e.g. free development) store is issued genuinely-signed webhook deliveries by Shopify. That user can:
1. Capture a valid `(raw_body, x-shopify-hmac-sha256)` pair for a webhook triggered on their own shop.
2. Replay that exact body + HMAC to the app's public webhook endpoint, but with `x-shopify-shop-domain` (and optionally `x-shopify-topic`/`x-shopify-webhook-id`) rewritten to point at a victim shop.
3. `HmacValidator.validate` still succeeds, because the signature only ever covered the body, and the secret is shared across all installs of the app.
4. `Registry.process` dispatches to the registered handler with `WebhookMetadata#shop` set to the attacker-chosen victim domain.

If the host application uses this `shop` value (as the gem's design encourages) to key which merchant's data/session/state to mutate (e.g., order fulfillment side effects, inventory adjustments, GDPR/compliance webhook processing, uninstall handling), the attacker can cause the app to attribute and act on forged data under a shop they do not control — a cross-tenant data/identity confusion originating purely from a gap in this gem's identity binding. This satisfies the "cross-tenant access" criterion.

### Likelihood Explanation
Exploitation requires only: (a) the ability to install the target app on any shop the attacker controls (trivial — free dev stores are self-serve), and (b) network access to the app's public webhook endpoint (which is public by design). No access token, `client_secret`, or privileged account is needed — only observation of one's own legitimately delivered webhook.

### Recommendation
Bind the header-derived identity fields into the signed material, or otherwise independently authenticate `shop`/`topic` before trusting them:
- Extend `VerifiableQuery#to_signable_string` for `Webhooks::Request` to include `shop`, `topic`, and `webhook_id` alongside the body (this requires coordinating with Shopify's signing scheme, since Shopify currently only signs the body — so alternatively, document/require that host apps re-verify the shop against their own installed-shop registry before trusting `WebhookMetadata#shop`), and/or
- Add explicit documentation/warnings in `docs/usage/webhooks.md` and on `WebhookMetadata#shop` that it is not itself HMAC-protected and must be cross-checked against the app's list of installed shops before being used to key any data mutation.

### Proof of Concept
```ruby
# 1. Attacker installs the target app on their own dev shop `attacker.myshopify.com`
#    and receives a real, validly-signed webhook, e.g.:
raw_body = '{"id":1,"note":"hello"}'
hmac = OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), app_client_secret, raw_body)
# (This is exactly what Shopify sends; attacker just captures it.)

# 2. Attacker replays it to the app's public webhook endpoint with a spoofed shop header
headers = {
  "x-shopify-topic" => "orders/create",
  "x-shopify-hmac-sha256" => Base64.encode64(hmac),   # still valid! same secret, same body
  "x-shopify-shop-domain" => "victim-shop.myshopify.com",  # attacker-controlled, not signed
  "x-shopify-webhook-id" => "forged-id",
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: headers)
ShopifyAPI::Webhooks::Registry.process(request)
# => HMAC check passes (Utils::HmacValidator.validate only checks raw_body)
# => handler.handle(data: WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...))
```
`Utils::HmacValidator.validate` at [4](#0-3)  compares only `verifiable_query.to_signable_string` (the body) against the received HMAC, so the forged `shop` header passes straight through untouched.

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
