### Title
Webhook `shop` identity field is trusted without being covered by the HMAC, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` validates only the raw webhook body against the HMAC, while the `shop` (tenant identity) field is read directly from an attacker-controllable HTTP header and is never part of the signed material. This breaks the intended binding `hmac == HMAC(secret, body ‖ shop)` down to `hmac == HMAC(secret, body)`, allowing a party who possesses one valid `(body, hmac)` pair to relabel it as belonging to a different shop.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop` is populated straight from the `x-shopify-shop-domain` / `shopify-shop-domain` header with no cross-check against the signed payload: [2](#0-1) 

`Registry.process` validates the HMAC via `Utils::HmacValidator.validate(request)`, which internally calls `to_signable_string` (body only) — the `shop` header plays no role in the signature check — and then forwards the untrusted `request.shop` straight into the handler-facing `WebhookMetadata`: [3](#0-2) [4](#0-3) 

`WebhookMetadata.shop` is a plain `String` field handed to the host application's `WebhookHandler#handle`, with no further verification available inside the gem: [5](#0-4) 

Because the HMAC secret (`client_secret`) is the same across every shop that has installed a given app, any actor who can obtain one legitimate `(raw_body, x-shopify-hmac-sha256)` pair for that app — e.g., by installing the app on their own store and observing/capturing a webhook delivery — can replay that exact body+HMAC to the app's webhook endpoint while substituting an arbitrary `x-shopify-shop-domain` header. `Utils::HmacValidator.validate` will still return `true` (it only checks the body), and `Registry.process` will hand the app a `WebhookMetadata` claiming the payload originated from a shop the attacker does not control.

This is exactly the "field acted on but not covered by the HMAC" bug class: the identity binding `shop (header, unauthenticated)` should equal `shop (implicitly bound into the signed payload)`, but the gem never enforces that equality.

### Impact Explanation
If the host application uses `WebhookMetadata#shop` to decide which merchant's records to update, delete, or query (a common pattern, e.g. `customers/redact`, `orders/create`, `app/uninstalled` handling), an attacker can cause the app to apply attacker-influenced webhook data to a victim shop's tenant context — a cross-tenant data-integrity/confusion issue. This meets the "cross-tenant access" bar in the High/Critical impact classes because the tenant (shop) boundary that the HMAC is supposed to protect is not actually bound to the value the application trusts for tenant identification.

### Likelihood Explanation
Exploitation requires only: (1) the ability to install the target app on an attacker-controlled store or otherwise capture one valid webhook body+HMAC for that app (trivial for any public/free app), and (2) the ability to send an arbitrary HTTP POST to the app's public webhook endpoint with a forged `shop-domain` header — both within reach of an unprivileged internet user with no access to `client_secret`, tokens, or credentials. The only constraint is finding a webhook `body` whose content is useful/replayable in the target's context, which is plausible for many webhook topics with attacker-influenced bodies (e.g., `app/uninstalled`, `shop/update`) or topics where body content matters less than the `shop` attribution itself.

### Recommendation
Bind the `shop` (and ideally `topic`, `api_version`, `webhook_id`) header values into the signed material used for HMAC verification, or otherwise cryptographically tie the shop identity to the verified payload before constructing `WebhookMetadata`. At minimum, `Utils::HmacValidator`/`Request#to_signable_string` should not allow tenant-identifying headers to bypass the signature check while still being propagated to application code as trusted data.

### Proof of Concept
1. Install the app on an attacker-owned development store (`attacker-shop.myshopify.com`) and trigger a webhook delivery (e.g., `app/uninstalled`), capturing the raw request body and the `x-shopify-hmac-sha256` header value sent by Shopify.
2. Replay this exact request to the same app's webhook endpoint, but replace the `x-shopify-shop-domain` header with `victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC over `request.to_signable_string` (the unchanged raw body) and succeeds, since `shop` is never part of the signed string: [6](#0-5) 
4. The handler receives `WebhookMetadata.new(... shop: "victim-shop.myshopify.com", ...)` even though the payload was never generated for that shop, demonstrating the broken `shop`-to-signature binding: [7](#0-6)

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

**File:** lib/shopify_api/webhooks/webhook_handler.rb (L6-24)
```ruby
    class WebhookMetadata < T::Struct
      const :topic, String
      const :shop, String
      const :body, T::Hash[String, T.untyped]
      const :api_version, String
      const :webhook_id, String
    end

    module WebhookHandler
      include Kernel
      extend T::Sig
      extend T::Helpers
      interface!

      sig do
        abstract.params(data: WebhookMetadata).void
      end
      def handle(data:); end
    end
```
