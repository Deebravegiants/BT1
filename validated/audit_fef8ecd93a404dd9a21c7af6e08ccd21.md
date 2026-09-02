Confirmed: the `shop`, `topic`, `webhook_id`, and `api_version` fields are all taken from unauthenticated HTTP headers and delivered to the app's handler via `WebhookMetadata`, while the HMAC only signs the raw body.### Title
Webhook `shop` (tenant) identity is not covered by the HMAC signature, enabling cross-tenant impersonation via header spoofing on a replayed webhook body - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC over the raw body only, while `shop`, `topic`, `webhook_id`, and `api_version` are read straight from HTTP headers that are never included in the signed material. `ShopifyAPI::Webhooks::Registry.process` validates only that HMAC and then forwards the header-derived `shop` value to the app's handler as trusted tenant identity, breaking the intended binding `shop_asserted == shop_that_produced(hmac)`.

### Finding Description
The webhook flow is:

1. `Request#to_signable_string` returns only the raw body: [1](#0-0) 

2. `Request#shop` (and `topic`, `webhook_id`, `api_version`) are pulled unauthenticated from headers: [2](#0-1) 

3. `HmacValidator.validate` verifies the HMAC using `verifiable_query.to_signable_string`, i.e., body-only: [3](#0-2) 

4. `Registry.process` checks only this body HMAC, then constructs `WebhookMetadata` directly from the unauthenticated `request.shop`, `request.topic`, etc., and hands it to the app's handler as the trusted tenant identifier: [4](#0-3) [5](#0-4) 

The identity binding the gem's own documentation promises is: "verify the request did indeed come from Shopify" and deliver `shop` as reliable tenant data to the handler (`docs/usage/webhooks.md`, "This will verify the request did indeed come from Shopify and then call the specified handler"). In practice the equality that should hold is:

`shop_delivered_to_handler == shop_that_the_HMAC_secret_owner_actually_signed_for`

But since `shop` is excluded from `to_signable_string`, the equality collapses to `hmac_valid == body_bytes_signed`, with `shop` completely decoupled from the signature. All shops on a given app share the same `api_secret_key` (Shopify apps use a single client secret across all shop installs), so a genuine, validly-signed webhook body captured from one shop's install can be replayed to the same public webhook endpoint with the `shop-domain` header (and even `topic`/`webhook-id`) changed to reference a different, victim shop. `HmacValidator.validate` still passes because it only checks the (unchanged) body against the (unchanged) HMAC; the forged `shop` value is never checked.

This exactly matches the reported bug class: "a field acted on but not covered by the HMAC" — here `shop` is acted upon (used as the tenant key handed to the app's `handle(data:)` callback) yet is not part of the signed payload.

### Impact Explanation
This is a High-severity cross-tenant identity-binding bypass. An attacker who legitimately installs the target app on their own (attacker-controlled) shop will receive genuine webhooks addressed to their shop, complete with a valid HMAC signed by the app's shared `api_secret_key`. Because `shop` is not part of the signed content, the attacker can resend that exact validly-signed request to the app's public webhook endpoint while substituting the `shopify-shop-domain` (and `shopify-topic`/`shopify-webhook-id`) header with an arbitrary victim shop's domain. `ShopifyAPI::Webhooks::Registry.process` will accept it as valid and dispatch it to the app's handler labeled as data belonging to the victim shop. Any app logic that trusts `WebhookMetadata#shop` to select per-tenant state, sessions, or storage (exactly as the gem's own documentation example does: `perform_later(topic: data.topic, shop_domain: data.shop, ...)`) will process attacker-controlled body content under another merchant's tenant context — a cross-tenant data-integrity/impersonation issue.

### Likelihood Explanation
Likelihood is meaningful but requires the attacker to have (or create) a legitimate installation of the target app to capture at least one validly HMAC-signed webhook payload for a topic of interest, and knowledge/guess of the target's `shop-domain` string (typically public, e.g. `victim.myshopify.com`). No access to `api_secret_key`, access tokens, or TLS interception is required — only observation of the attacker's own genuine webhook traffic and the ability to POST a modified copy to the same public endpoint, both of which are available to any unprivileged internet user who can install the app.

### Recommendation
Include the tenant-identifying headers (`shop`, and ideally `topic`/`webhook_id`) in the HMAC-signed material, or verify them against an independent trusted channel (e.g., cross-check `shop` against a shop for which the app holds an active session/registration and reject if not matching an expected pending webhook) before constructing `WebhookMetadata`. At minimum, bind `shop` cryptographically into `to_signable_string` in `lib/shopify_api/webhooks/request.rb` so `HmacValidator.validate` fails if the shop header is altered relative to the signed body.

### Proof of Concept
1. Attacker installs the target Shopify app on `attacker-shop.myshopify.com`.
2. Attacker triggers a webhook event (e.g., `orders/create`) and captures the resulting genuine POST request to the app's webhook endpoint, including headers `x-shopify-hmac-sha256: <valid-hmac>`, `x-shopify-shop-domain: attacker-shop.myshopify.com`, and the raw JSON body.
3. Attacker replays this exact request to the same endpoint but changes only `x-shopify-shop-domain` to `victim-shop.myshopify.com` (leaving body and HMAC header untouched).
4. `ShopifyAPI::Webhooks::Request#hmac` and `#to_signable_string` compute over the unchanged raw body; `Utils::HmacValidator.validate` succeeds because the HMAC still matches the body [6](#0-5) .
5. `Registry.process` calls the handler with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...)`, and the app's business logic (per the gem's documented example) processes attacker-supplied data as belonging to `victim-shop.myshopify.com` [7](#0-6) .

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-13)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end
```

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
