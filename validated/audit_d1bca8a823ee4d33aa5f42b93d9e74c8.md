### Title
Webhook shop-domain header is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`Registry.process` authenticates an incoming webhook solely via `Utils::HmacValidator.validate(request)`, which recomputes the HMAC over `request.to_signable_string` — the raw request body only. The `shop`, `topic`, `api_version`, and `webhook_id` values are pulled straight from HTTP headers that are never part of the signed bytes. As a result, a valid HMAC only proves the body was signed by Shopify with the app's `client_secret`; it does not bind that body to the `shop-domain` header that the handler ultimately trusts.

### Finding Description
`Webhooks::Request#to_signable_string` returns `@raw_body` only [1](#0-0) , and `shop` is read directly from the `x-shopify-shop-domain`/`shopify-shop-domain` header with no cryptographic tie to the HMAC [2](#0-1) . `Utils::HmacValidator.validate` only checks `verifiable_query.to_signable_string` (the body) against the computed signature, ignoring headers entirely [3](#0-2) . `Registry.process` then raises only if the HMAC fails, and afterwards constructs `WebhookMetadata` using `request.shop` taken from the unauthenticated header [4](#0-3) , which is handed directly to the app's `WebhookHandler#handle` as the merchant/tenant identity for that event [5](#0-4) .

The broken identity binding, stated as an equality that should hold but doesn't:
`shop authenticated by HMAC == shop delivered to WebhookHandler#handle`

Before the attack: legitimate webhook for shop A arrives with body B, `x-shopify-shop-domain: A`, and `hmac = HMAC(secret, B)`. HMAC validation passes; `request.shop == "A"`, consistent with the signed content's actual source.

Attacker's request sequence: the attacker owns/controls an app installation on their own store (or otherwise captures one valid `(body, hmac)` pair from any shop using the app) and replays the exact same `raw_body`/`hmac` pair to the app's webhook endpoint while substituting `x-shopify-shop-domain: VICTIM_SHOP`. `HmacValidator.validate` still passes because `to_signable_string` is unchanged and the signature only covers the body bytes, not the header [6](#0-5) .

After the attack: `request.shop == "VICTIM_SHOP"` even though the HMAC-signed body never originated from Shopify for that shop. `Registry.process` passes this forged `shop` value straight into the handler with no additional check [4](#0-3) .

### Impact Explanation
This lets an attacker who has captured or triggered any single valid webhook delivery (e.g. by installing the app on their own store) forge webhook events attributed to any other merchant using the app, since `shop` is fully attacker-controlled and unauthenticated. Depending on how the host application keys its business logic off `WebhookMetadata#shop` (e.g. `orders/create`, `app/uninstalled`, mandatory GDPR topics like `shop/redact` or `customers/redact`), this enables cross-tenant data injection or triggering merchant-affecting workflows (including data-deletion mandatory webhooks) against a shop the attacker does not control. This crosses the tenant boundary the SDK is responsible for enforcing when handing verified webhook data to the host app, matching the "cross-tenant access" impact category.

### Likelihood Explanation
Likelihood is Low-to-Medium: the attacker must obtain at least one legitimately HMAC-signed webhook body/signature pair for the target app (trivially available to anyone who installs the app on a free/dev store), and must know or guess a valid target shop domain (often discoverable, e.g. via the app's own OAuth flow or public storefront). No possession of the `client_secret` or access token is required — only header manipulation of an HTTP POST to the app's own webhook endpoint.

### Recommendation
Include the `shop-domain` (and ideally `topic`/`webhook-id`) header values in the signed material verified by `HmacValidator`, or otherwise cryptographically bind the header-derived `shop` to the HMAC-verified body before constructing `WebhookMetadata` in `Registry.process`. At minimum, document/require host applications to cross-check `WebhookMetadata#shop` against an independently known/authorized shop list rather than trusting it implicitly, since today `to_signable_string` in `lib/shopify_api/webhooks/request.rb` only signs `@raw_body`.

### Proof of Concept
1. Install the target app on attacker-owned store `attacker-shop.myshopify.com`; capture a real webhook delivery, e.g. for `orders/create`, noting the exact `raw_body` and `x-shopify-hmac-sha256` value Shopify sent.
2. Replay an HTTP POST to the app's webhook endpoint with the identical `raw_body` and `x-shopify-hmac-sha256`, but set `x-shopify-shop-domain: victim-shop.myshopify.com` and `x-shopify-topic: shop/redact` (or another topic of interest).
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)` [7](#0-6) ; this passes because `to_signable_string` is unchanged from step 1.
4. `Registry.process` invokes the registered handler with `WebhookMetadata.new(... shop: request.shop ...)`, where `request.shop == "victim-shop.myshopify.com"` [8](#0-7)  — the app now processes attacker-supplied data/events as if they originated from the victim shop.

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
