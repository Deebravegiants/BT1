## Finding

The webhook signature verification in this gem authenticates the request body, but not the shop-domain (or topic) header that the library then hands to the app as the tenant identifier. Because Shopify webhook HMACs are computed with an app-level secret (`Context.api_secret_key`) that is identical across every shop that has the app installed, an attacker who controls one shop (a legitimate install) can capture a validly-signed webhook and replay it to the same endpoint after swapping the shop-domain header — the signature still checks out because that header is never covered by the HMAC.

### Title
Webhook shop-domain header not covered by HMAC allows cross-tenant webhook forgery - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw body, so `ShopifyAPI::Utils::HmacValidator.validate` (used in `ShopifyAPI::Webhooks::Registry.process`) verifies the payload integrity but not the identity of the shop the webhook claims to be from.

### Finding Description
`Request#to_signable_string` is defined as: [1](#0-0) , which returns only `@raw_body`. The `shop` accessor, however, is read straight from the `shopify-shop-domain`/`x-shopify-shop-domain` header with no cryptographic binding: [2](#0-1) .

`Registry.process` validates only the HMAC of the body, then forwards `request.shop` unchecked to the app's handler as the tenant identifier: [3](#0-2) .

The HMAC secret (`Context.api_secret_key`) is the app's single `client_secret`, shared across all shops that install the app — it is not shop-specific: [4](#0-3) .

The identity binding that should hold is: `shop header == shop that the HMAC-signed body actually belongs to`. Because the shop header is excluded from the signed content, this equality is never checked. An unprivileged user who legitimately installs the app on their own store (shop A) can capture any real webhook Shopify sends them (valid HMAC over the body, computed with the app's one shared secret) and resend that exact `(raw_body, hmac)` pair to the app's webhook endpoint while substituting the `shopify-shop-domain` header with a victim shop B's domain. `HmacValidator.validate` still passes (it only checks the body/secret pair), and `Registry.process` dispatches the handler with `shop: "victim-shop.myshopify.com"`, `topic`, and attacker-chosen `body` content, effectively forging a webhook attributed to a tenant the attacker does not control.

### Impact Explanation
This breaks the tenant boundary the gem is supposed to enforce for webhook consumers: an attacker with only a legitimate installation of the app on their own shop can inject forged webhook events "from" any other shop that also has the app installed, since the shop domain carries no authentication of its own. Depending on how the host app's webhook handlers use `WebhookMetadata#shop` (e.g., to look up/act on that merchant's data), this is a cross-tenant data-integrity/access issue — matching the "cross-tenant access" impact category.

### Likelihood Explanation
Requires only an app install on an attacker-controlled shop (no special privileges, no leaked secrets) plus intercepting one legitimate webhook delivery from Shopify to that shop — both trivially available to any developer/merchant who installs the app. No `client_secret`, access token, or TLS interception is needed since the attacker never needs to produce a valid HMAC themselves; they only replay one they already legitimately received.

### Recommendation
Include the shop domain (and topic/webhook-id, if they must be trusted) in the HMAC-signed content, or otherwise cryptographically bind the `shop` header to the request/body before it is trusted (e.g., verify a per-shop identifier or reconcile it against session/shop records maintained by the app) rather than accepting it as unauthenticated header data whenever it's forwarded to consumers as the tenant identity.

### Proof of Concept
1. Attacker installs the app on `attacker-shop.myshopify.com` (a normal, permitted install).
2. Shopify sends a legitimate webhook to the app's endpoint with headers `x-shopify-shop-domain: attacker-shop.myshopify.com`, `x-shopify-topic: orders/create`, a valid `x-shopify-hmac-sha256`, and some `raw_body`.
3. Attacker captures this request, then resends it to the same endpoint changing only `x-shopify-shop-domain` to `victim-shop.myshopify.com` (or fabricates a new body of their choosing and simply keeps the correct HMAC/body pairing while varying the shop header, since shop isn't part of the signed content).
4. `ShopifyAPI::Webhooks::Registry.process` → `Utils::HmacValidator.validate(request)` returns `true` (body+secret unchanged), and the handler is invoked with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", topic: ..., body: ...)`, per [5](#0-4) .

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-22)
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
```
