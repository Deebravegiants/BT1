I have enough evidence to finalize the analysis.

### Title
Webhook `shop-domain` identity is not bound by the HMAC signature, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` computes and validates the HMAC over the raw request body only, while the `shop`, `topic`, `webhook_id`, and `api_version` values that are handed to the app's webhook handler are read directly from unauthenticated HTTP headers. The `shop` value is never covered by the HMAC, so any party who possesses one valid `(body, hmac)` pair can replay it to the app's public webhook endpoint while substituting an arbitrary `x-shopify-shop-domain` header, and `Registry.process` will pass that attacker-chosen shop identity to the handler as authenticated.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

The `shop`, `topic`, `api_version`, and `webhook_id` accessors are all pulled straight from request headers with no cryptographic binding to the signed body: [2](#0-1) 

`Utils::HmacValidator.validate` verifies `verifiable_query.hmac` against `HMAC(secret, to_signable_string)`, i.e. it only proves the *body* bytes were signed by someone holding `api_secret_key` (Shopify) — it says nothing about which shop the body belongs to: [3](#0-2) 

`Registry.process` then forwards the unauthenticated `request.shop` straight into `WebhookMetadata` and into the app's handler, alongside the topic/webhook_id/api_version that are equally unauthenticated: [4](#0-3) 

`WebhookMetadata.shop` is a plain `String` field with no further validation performed downstream in this gem: [5](#0-4) 

The identity binding broken is:
`shop bound by HMAC (expected)` ≠ `shop parsed from x-shopify-shop-domain header (actual)`.

Concretely: an unprivileged internet user who runs their own Shopify store and has this same app installed on it will legitimately receive real, correctly-signed webhooks from Shopify for their own shop (valid `(raw_body, hmac)` pairs, since the HMAC is computed purely from body + the app's shared secret, which such a merchant is not expected to know but can *observe* signed traffic for their own tenant). That attacker can capture such a legitimate `(body, hmac)` pair and POST it directly to the target app's public webhook endpoint, keeping `x-shopify-hmac-sha256` and the body untouched but rewriting `x-shopify-shop-domain` to the victim shop's domain (and optionally the topic/webhook-id headers). `HmacValidator.validate` still succeeds because it only checks the body, so `Registry.process` calls the handler with `shop: "victim-shop.myshopify.com"` even though the payload content actually originates from the attacker's own store.

### Impact Explanation
Any consuming app that trusts `WebhookMetadata#shop` as the tenant key (e.g., to look up the stored session/access token for that shop, write records scoped by shop, or trigger shop-specific business logic) can be made to associate attacker-supplied webhook data with a shop the attacker does not own — a cross-tenant confusion driven entirely by this gem's failure to bind the `shop` field to the cryptographic proof it exposes as "verified." This satisfies the Critical "cross-tenant access" impact category, because the app-facing API of this gem (`Registry.process` / `WebhookMetadata`) presents `shop` as if it had been authenticated by the preceding HMAC check, when it has not been.

### Likelihood Explanation
Any user of the target app who is themselves a legitimate Shopify merchant (i.e., any internet user who installs the same publicly-listed app on their own store) can obtain a valid `(body, hmac)` pair for at least one webhook topic without needing the app's `api_secret_key`, since Shopify itself will deliver that pair to them. Replaying it against the same app's shared HTTP webhook endpoint with a modified shop header requires only basic HTTP tooling — no credential theft, TLS interception, or social engineering is needed.

### Recommendation
Include the shop domain (and topic/webhook id, if they are relied upon) in the signable content that is validated, or cross-check `request.shop` against a value obtained from a source not controllable by the requester (e.g., correlate against the currently registered shop for that webhook subscription/session store) before trusting it in `WebhookMetadata`. At minimum, document prominently that `WebhookMetadata#shop` is unauthenticated and must not be used as a trust boundary by consuming apps, and consider having `Registry.process` reject/require an explicit application-level shop verification step.

### Proof of Concept
1. Attacker installs the vulnerable app on `attacker.myshopify.com` and configures a webhook subscription (e.g. `orders/create`).
2. Shopify delivers a real webhook to the app's endpoint with headers:
   - `x-shopify-hmac-sha256: <valid HMAC of raw body using app secret>`
   - `x-shopify-shop-domain: attacker.myshopify.com`
   - raw body: JSON order payload
3. Attacker captures the exact `raw_body` and `x-shopify-hmac-sha256` value (they can observe this on their own infrastructure/proxy since it is delivered to their own endpoint).
4. Attacker crafts a new HTTP POST to the same app's webhook endpoint, keeping `raw_body` and `x-shopify-hmac-sha256` identical, but sets `x-shopify-shop-domain: victim.myshopify.com`.
5. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only checks `HMAC(secret, raw_body)`: [3](#0-2) 
6. The handler is invoked with `WebhookMetadata.new(topic: ..., shop: "victim.myshopify.com", body: <attacker's order data>, ...)`: [6](#0-5) 
7. Any host application logic keyed on `data.shop` (session lookup, per-shop data writes, notifications) now operates as if this attacker-controlled payload genuinely originated from `victim.myshopify.com`.

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
