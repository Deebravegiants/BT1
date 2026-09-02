This confirms the finding: `Webhooks::Request#to_signable_string` returns only `@raw_body`, while `Webhooks::Request#shop`, `#topic`, and `#webhook_id` are read straight from unauthenticated HTTP headers via `shopify_header` and are never part of the HMAC-signed material.### Title
Webhook shop-domain header not bound to HMAC signature, allowing cross-tenant shop spoofing on replay - ([File: lib/shopify_api/webhooks/request.rb](lib/shopify_api/webhooks/request.rb))

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by verifying an HMAC over the raw request body, but the `shop` (and `topic`/`webhook_id`) values that the app's handler subsequently trusts are taken from unauthenticated HTTP headers that are never covered by that HMAC.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Webhooks::Request#shop`, `#topic`, and `#webhook_id` are read directly from HTTP headers with no cryptographic tie to the signed payload: [2](#0-1) 

`Registry.process` validates the webhook using only `Utils::HmacValidator.validate(request)`, which internally calls `verifiable_query.to_signable_string` (i.e. the raw body) and compares it against `HMAC(secret, raw_body)`: [3](#0-2) [4](#0-3) 

After this check passes, `Registry.process` builds a `WebhookMetadata` struct straight from `request.shop`, which is the unauthenticated header value, and hands it to the app's `WebhookHandler#handle`: [5](#0-4) [6](#0-5) 

The broken identity binding is:
`shop_authenticated_by_hmac (∅, not part of signable string) ≠ shop_used_by_handler (Request#shop, from header)`

Because `Context.api_secret_key` is a single shared secret for the whole app (used for every merchant that has the app installed) rather than a per-shop secret, any merchant who installs the app can trigger a genuine webhook to obtain a valid `(body, hmac)` pair signed with that shared secret. That attacker — an unprivileged internet user with respect to any other merchant's tenant — can then replay the exact same body/HMAC pair to the app's public webhook endpoint while substituting the `x-shopify-shop-domain` (and/or `x-shopify-topic`, `x-shopify-webhook-id`) header to name a victim shop. `HmacValidator.validate` still succeeds because it only checks the body, and `Registry.process` dispatches the handler with `data.shop` set to the spoofed victim shop and `data.body` set to attacker-controlled content.

### Impact Explanation
This breaks the shop/tenant identity binding at the point applications rely on it most: any app built on this gem's webhook handler receives `WebhookMetadata#shop` as an authenticated fact. In reality, an attacker who has one legitimate app installation can forge convincing webhook deliveries appearing to originate from any other merchant shop, letting them inject attacker-chosen data (order/customer/product payloads, etc.) into another tenant's processing pipeline — a cross-tenant confused-deputy condition. Depending on what the host app does with webhook data (e.g., writing to per-shop records keyed by `data.shop`, triggering side effects, or feeding into decisions gated by shop identity), this can corrupt or leak another tenant's state.

### Likelihood Explanation
Requires the attacker to have (or create) their own shop installation of the target app to obtain one valid `(body, hmac)` pair — a low bar since app installation is self-service for merchants and does not require any privileged credentials from the victim. The webhook endpoint is a public internet endpoint by design (Shopify calls it externally), so replaying the captured request with a modified header is straightforward and requires no secrets.

### Recommendation
Bind the `shop` (and `topic`/`webhook_id`) values into the HMAC-verified material, or otherwise authenticate them independently — e.g., include them in `to_signable_string`, or require the caller to also validate the request source registered with Shopify per-shop mapping stored in the app's own webhook subscription records, instead of trusting the header value as an established fact once body-HMAC passes.

### Proof of Concept
1. Attacker installs the target app on shop `attacker.myshopify.com`, triggering a real webhook delivery. They capture the raw body `B` and the `x-shopify-hmac-sha256` header `H` for a topic of interest (both valid against the app's shared `api_secret_key`).
2. Attacker sends a forged POST request directly to the app's public webhook endpoint with:
   - body: `B` (unchanged)
   - `x-shopify-hmac-sha256: H` (unchanged, still valid since HMAC only covers the body)
   - `x-shopify-shop-domain: victim-shop.myshopify.com` (spoofed)
   - `x-shopify-topic`, `x-shopify-webhook-id` as desired
3. `ShopifyAPI::Webhooks::Request.new` accepts the headers, `Utils::HmacValidator.validate` succeeds (per `lib/shopify_api/utils/hmac_validator.rb:26-31`, computed only over `@raw_body`).
4. `Registry.process` (`lib/shopify_api/webhooks/registry.rb:189-199`) invokes the app's handler with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: <attacker's body>, ...)`, causing the app to process attacker-controlled data as if it belonged to the victim shop.

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
