### Title
Webhook shop identity is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` derives the merchant identity (`shop`) exclusively from the `X-Shopify-Shop-Domain` HTTP header, while the HMAC signature verified by `Utils::HmacValidator` only covers the raw request body via `to_signable_string`. The `shop` value that is handed to the host application's webhook handler (and used to key/select tenant data) is never part of the signed material.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) . `Utils::HmacValidator.validate_signature` computes the HMAC over exactly that signable string and compares it to the `hmac-sha256` header: [2](#0-1) .

Meanwhile, `Request#shop` is read straight from the unauthenticated `shopify-shop-domain`/`x-shopify-shop-domain` header with no cryptographic binding to the body or to the HMAC: [3](#0-2) .

`Registry.process` validates only the HMAC over the body, then dispatches to the registered handler using `request.shop` as the tenant identity that the handler will act on: [4](#0-3) . The resulting `WebhookMetadata` struct — which host applications use to attribute the webhook payload to a specific merchant — carries this unauthenticated `shop` field verbatim: [5](#0-4) .

This is exactly the identity-binding break called out in the rules: **a field acted on (`shop`) but not covered by the HMAC**. Because the HMAC is computed only over `@raw_body`, an attacker who possesses one valid `(raw_body, hmac)` pair from any webhook delivery (their own store, a shared/public topic payload, or any previously observed delivery for the app) can replay that exact body/HMAC pair while substituting an arbitrary value for the `X-Shopify-Shop-Domain` header. `HmacValidator.validate` will still return `true` because the signature check never inspects the shop header: [6](#0-5) . The gem then hands the handler a `WebhookMetadata` claiming the forged shop, with a body the attacker fully controls in shape (any JSON body he could get legitimately HMAC-signed, e.g. from his own test/dev shop) but with attacker-chosen shop attribution.

Before the attacker's request: `shop_claimed == shop_that_produced(hmac)`. After the forged request: `shop_claimed != shop_that_produced(hmac)`, yet the gem still treats the request as authentic for `shop_claimed` because `HmacValidator.validate` verifies `raw_body` and `hmac` only, never `shop`.

### Impact Explanation
Any host application built on this gem that uses `WebhookMetadata#shop` (or `Registry.process`'s dispatch) to select which merchant's data record to create/update/delete is vulnerable to cross-tenant data injection/corruption: an attacker registers a webhook subscription on a shop they control (or otherwise obtains one valid signed body+HMAC pair for this app's endpoint), then replays that body with a different shop header pointed at a victim merchant. This satisfies the "Critical – cross-tenant access" bar because it breaks the binding between the cryptographic proof of authenticity and the tenant the payload is attributed to.

### Likelihood Explanation
Likelihood is high for exploitation preconditions: obtaining one legitimately signed `(body, hmac)` pair only requires the attacker to install/develop the same app on any shop (including their own development store) and observe a webhook delivery, which is normal, low-privilege access for any app developer/merchant — no `api_secret_key`, access token, or privileged account is required. The forged header swap is a simple HTTP replay.

### Recommendation
Bind the `shop` (and ideally `topic`/`webhook_id`) into the value that is HMAC-verified, or independently verify that the shop asserted in the header actually owns an active installation/session for this app before dispatching to the handler, instead of trusting the header once only the body-HMAC has passed.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and triggers a webhook for a subscribed topic (e.g., `orders/create`), capturing the raw body `B` and the valid `X-Shopify-Hmac-Sha256: H` computed by Shopify with the app's real `client_secret`.
2. Attacker crafts a new HTTP POST to the app's webhook endpoint with the same body `B` and header `X-Shopify-Hmac-Sha256: H`, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` parses this into `raw_body = B`, `shop = "victim-shop.myshopify.com"`.
4. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC over `B` only and matches `H`, returning `true`. [7](#0-6) 
5. The handler receives `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: parsed(B), ...)` and performs its normal processing (e.g., writing order data) under the victim shop's identity, even though the payload never originated from or was authorized by that shop.

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
