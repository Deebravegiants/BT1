## Title
Webhook `shop` (and `topic`/`webhook_id`/`api_version`) is not covered by the HMAC signature, enabling cross-tenant webhook replay/spoofing - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by HMAC-verifying the raw request body, then unconditionally forwards the `shop-domain` header (along with `topic`, `webhook_id`, `api_version`) to the app's handler as trusted, verified tenant identity. None of these header fields are included in the HMAC computation, so the binding "HMAC-verified data == data attributed to a shop" does not hold.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

while `shop`, `topic`, `webhook_id`, and `api_version` are all read straight from HTTP headers with no cryptographic binding to the body or to each other: [2](#0-1) 

`Registry.process` validates only the HMAC (i.e., only the body) via `Utils::HmacValidator.validate(request)`, and then immediately builds `WebhookMetadata` from the request's `shop`, `topic`, `webhook_id`, `api_version` fields and calls the app-supplied handler with it: [3](#0-2) 

`Utils::HmacValidator.validate` computes the signature purely over `verifiable_query.to_signable_string` (the raw body) using the app's shared `api_secret_key` — the same secret is used for every shop that has the app installed: [4](#0-3) 

The equality broken: `shop bound by HMAC (∅)` != `shop attributed to the webhook payload passed to the handler (request.shop, an unauthenticated header)`. Because the same app-level secret signs webhooks for all merchants, an unprivileged user who installs the app on their own store can legitimately receive a Shopify webhook (valid body + valid HMAC), capture it, and replay it against the app's webhook endpoint while substituting the `x-shopify-shop-domain` header for a victim shop. The HMAC check still passes (it only verifies the body), and `Registry.process` will call the handler with `WebhookMetadata.shop` set to the forged victim domain and the attacker's body content.

The gem's own documentation reinforces the false assumption that `process` fully authenticates the request's origin/identity: "This will verify the request did indeed come from Shopify and then call the specified handler for that webhook" — but only the body's origin is verified, not the shop attribution. [5](#0-4) 

### Impact Explanation
This crosses a tenant boundary: an attacker who is a legitimate (unprivileged) merchant on the same app can inject data attributed to a different merchant's shop into the host application via the webhook handler (e.g., forged `orders/create` data appearing to belong to a victim shop, if the host app trusts `data.shop` to select which tenant's records to create/update, as the gem's own docs example does: `perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)`). This matches the "cross-tenant access" Critical impact category, since the gem hands the host app attacker-controlled tenant identity as if it were Shopify-verified.

### Likelihood Explanation
Requires only: (1) the attacker installs the target app on their own Shopify store (standard, unprivileged action for any app targeting the App Store or public install), (2) they trigger a webhook event on their own store and capture the body + `X-Shopify-Hmac-Sha256` value from the delivery to their own endpoint, (3) they replay that exact body/HMAC pair to the app's public webhook endpoint with a modified `X-Shopify-Shop-Domain` header. No secrets, tokens, or privileged access are needed beyond operating one's own shop — a capability any internet user can obtain by installing a public app.

### Recommendation
Do not treat header-derived fields (`shop`, `topic`, `webhook_id`, `api_version`) as authenticated. At minimum:
- Include the shop domain (and ideally topic/webhook id) in the HMAC-signable string, or
- Require the host application to independently verify that the `shop` in `WebhookMetadata` corresponds to a shop with a currently valid, matching webhook subscription/session before acting on the payload, and document this requirement prominently in `docs/usage/webhooks.md`, or
- Bind webhook processing to a per-shop secret model instead of a single app-wide `api_secret_key`, if/when Shopify's webhook delivery mechanism supports it.

### Proof of Concept
1. Attacker installs the target Shopify app on `attacker-shop.myshopify.com` and configures/observes a webhook subscription (e.g. `orders/create`) pointing at the app's public webhook URL.
2. Attacker triggers the event (e.g. creates an order) and captures the exact raw request body `B` and the `X-Shopify-Hmac-Sha256: H` header Shopify sent to the app.
3. Attacker replays an HTTP POST to the same app webhook endpoint with body `B`, header `X-Shopify-Hmac-Sha256: H` (unchanged — still valid, since HMAC only covers `B` and app secret is shared across shops), and header `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: {...})` is constructed; `Utils::HmacValidator.validate` succeeds because it only checks `B` against `H`.
5. `Registry.process` calls the handler with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: parsed(B), ...)`, causing the host app to process attacker-controlled data under the victim shop's tenant identity.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery).returns(T::Boolean) }
        def validate(verifiable_query)
          return false unless verifiable_query.hmac

          result = validate_signature(verifiable_query, Context.api_secret_key)
          if result || Context.old_api_secret_key.nil? || T.must(Context.old_api_secret_key).empty?
            result
          else
            validate_signature(verifiable_query, T.must(Context.old_api_secret_key))
          end
        end

        private

        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

**File:** docs/usage/webhooks.md (L123-125)
```markdown
## Process a Webhook

To process an http webhook, you need to listen on the route(s) you provided during the Webhook registration process, then when the route is hit construct a `ShopifyAPI::Webhooks::Request` and call `ShopifyAPI::Webhooks::Registry.process`. This will verify the request did indeed come from Shopify and then call the specified handler for that webhook. An example in Rails is shown below:
```
