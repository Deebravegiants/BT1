### Title
Webhook `shop`, `topic`, `webhook_id`, and `api_version` are trusted from unauthenticated headers while only the raw body is HMAC-verified - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` is documented to "verify the request did indeed come from Shopify" before dispatching it to the app's handler, but the HMAC signature only covers the raw request body. The `shop`, `topic`, `webhook_id`, and `api_version` values — all sourced from HTTP headers — are never bound to the HMAC and are handed to the app's handler as trusted, verified data.

### Finding Description
`ShopifyAPI::Webhooks::Request` implements `Utils::VerifiableQuery`, whose `to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop`, `topic`, `webhook_id`, and `api_version` are all pulled directly from HTTP headers, none of which participate in the signable string: [2](#0-1) 

`HmacValidator.validate` computes the signature purely from `verifiable_query.to_signable_string` (i.e., the body) and compares it against the `hmac` header: [3](#0-2) 

`Registry.process` treats a passing HMAC check as full authentication of the request, then immediately forwards the unauthenticated header-derived `shop`, `topic`, `webhook_id`, and `api_version` fields to the app's handler as `WebhookMetadata`: [4](#0-3) [5](#0-4) 

The library's own documentation instructs developers to trust these exact fields as verified tenant/event identifiers coming out of `process`: [6](#0-5) [7](#0-6) 

This breaks the identity binding `hmac(shop, topic, body) == request.shop` — instead, the gem only checks `hmac(body) == valid`, then separately trusts `request.shop`/`request.topic` from headers with no cryptographic tie to the verified body. An unprivileged internet user who can obtain one genuine `(raw_body, hmac)` pair signed with the app's `client_secret` — trivially available by installing the target app on their own Shopify development store and having Shopify deliver a real webhook to them — can replay that exact body+hmac directly to the app's public webhook endpoint while substituting an arbitrary `shopify-shop-domain` header (and/or `shopify-topic`/`shopify-webhook-id`). `HmacValidator.validate` still passes because it only checks the body, and `Registry.process` calls the handler with the attacker-chosen `shop`/`topic` values, which `WebhookMetadata` and the documentation both present as verified. Any app whose handler uses `data.shop` for tenant identification (exactly as shown in the gem's own example code) will process forged data under an arbitrary victim shop's identity.

### Impact Explanation
This is a cross-tenant identity-binding break: an attacker who owns any shop with the app installed can inject a "verified" webhook event attributed to a different, victim shop, without ever obtaining the victim's credentials or the app's `client_secret`. Depending on the handler logic (as recommended in the gem's own docs, e.g. `perform_later(shop_domain: data.shop, ...)`), this can lead to cross-tenant data corruption, spoofed order/customer events being applied to the wrong merchant, or triggering merchant-scoped side effects (installs/uninstalls, GDPR webhooks, etc.) under a false shop identity — satisfying the "Critical: cross-tenant access" impact bar.

### Likelihood Explanation
Likelihood is moderate-to-high: the attacker only needs to install the target app (many apps have public/free installs or dev-store distribution) to receive one legitimate signed webhook, then can replay it indefinitely with a forged `shop`/`topic` header directly to the app's public webhook endpoint. No access to `api_secret_key`, access tokens, or the victim's environment is required — matching the "unprivileged internet user" threat model.

### Recommendation
Bind the security-relevant identity fields into the HMAC computation (or otherwise cryptographically tie header values to the payload before trusting them), or clearly document/enforce that `shop`, `topic`, `webhook_id`, and `api_version` returned in `WebhookMetadata` are unauthenticated and must be independently corroborated by the host app (e.g., cross-checked against an existing session/shop record) before being used for tenant-scoped actions. At minimum, update `docs/usage/webhooks.md` to stop presenting `process` as verifying the full request, and clarify exactly which fields are covered by the HMAC.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker.myshopify.com`, triggers an event (e.g., `orders/create`), and captures the real webhook Shopify sends: raw body `B` and header `x-shopify-hmac-sha256: H` (valid HMAC of `B` with the app's `client_secret`).
2. Attacker sends a POST directly to the app's public webhook endpoint with:
   - Body: `B` (unmodified)
   - `x-shopify-hmac-sha256: H` (unmodified, valid)
   - `x-shopify-shop-domain: victim.myshopify.com` (forged)
   - `x-shopify-topic: orders/create` (unchanged or forged)
3. `ShopifyAPI::Webhooks::Request.new` accepts the forged headers, `Utils::HmacValidator.validate` passes because only `B` is checked, and `Registry.process` calls the handler with `WebhookMetadata(shop: "victim.myshopify.com", topic: "orders/create", body: parsed B, ...)`.
4. The handler processes attacker-controlled event data as if it belonged to `victim.myshopify.com`, per the gem's documented usage pattern.

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

**File:** docs/usage/webhooks.md (L12-17)
```markdown
`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
- `body`, `T::Hash[String, T.untyped]`- The body of the webhook
- `webhook_id`, `String` - The id of the webhook event to [avoid duplicates](https://shopify.dev/docs/apps/webhooks/best-practices#ignore-duplicates)
- `api_version`, `String` - The api version of the webhook
```

**File:** docs/usage/webhooks.md (L123-125)
```markdown
## Process a Webhook

To process an http webhook, you need to listen on the route(s) you provided during the Webhook registration process, then when the route is hit construct a `ShopifyAPI::Webhooks::Request` and call `ShopifyAPI::Webhooks::Registry.process`. This will verify the request did indeed come from Shopify and then call the specified handler for that webhook. An example in Rails is shown below:
```
