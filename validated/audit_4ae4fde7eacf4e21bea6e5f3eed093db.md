### Title
Webhook `shop-domain` header is trusted by handlers without being covered by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its signable string from the raw HTTP body only, while the `shop`, `topic`, and `webhook_id` values are taken from separate, unsigned HTTP headers. `Registry.process` validates the HMAC against the body but then hands the caller-supplied `shop` header straight to the app's handler as the authoritative tenant identity, breaking the binding `shop authenticated == shop the HMAC covers`.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop`, `#topic`, and `#webhook_id` are pulled from HTTP headers that are never part of the signed payload: [2](#0-1) 

`Registry.process` validates the HMAC using `Utils::HmacValidator.validate(request)`, which internally calls `verifiable_query.to_signable_string` (i.e., the raw body) and compares it against the `hmac` field, but never checks the `shop` header against anything: [3](#0-2) [4](#0-3) [5](#0-4) 

Once the HMAC over the body succeeds, `process` forwards `request.shop` (attacker-controllable header, not covered by the signature) directly into `WebhookMetadata`, which the app's handler treats as the authoritative tenant for the event: [6](#0-5) 

Because the same `api_secret_key` (the app's client secret, shared across every merchant that installs the app) is used to sign every shop's webhook body, a merchant who installs the app for their own store (`attacker-shop.myshopify.com`) can legitimately receive a validly-HMAC-signed webhook body for that shop. They can then replay that exact body/HMAC pair to the app's webhook endpoint while substituting the `X-Shopify-Shop-Domain` header for a different, victim merchant's domain. The HMAC check passes (it only verifies the body), but the handler executes believing the event originated from the victim shop, i.e., `shop authenticated (by header) != shop bound by signature (none)`.

### Impact Explanation
This breaks the tenant-isolation guarantee webhook consumers rely on: a merchant/attacker who is a legitimate but unprivileged user of the app for their own store can forge webhook events "from" any other shop that also uses the app, without needing that shop's credentials, access token, or `client_secret`. Depending on how the host app trusts `WebhookMetadata#shop` (e.g., to look up per-shop settings, trigger fulfillment actions, or update per-tenant state), this enables cross-tenant data manipulation or disclosure — classified as Critical (cross-tenant access) per the scope rules.

### Likelihood Explanation
Likelihood is moderate-to-high for apps that: (1) register the same webhook topic across many merchants (topics like `app/uninstalled`, `shop/update`, or any topic with attacker-influenceable body content are good candidates), and (2) trust `WebhookMetadata#shop` for authorization or tenant-scoped writes without any additional binding (e.g., without independently verifying the shop is the one that installed with the given `webhook_id`, or without maintaining a webhook_id→shop registry checked before acting). Any developer using this gem's documented `Registry.process` API as intended is exposed, since the gem itself performs no shop/HMAC binding check — this is not a misuse of an undocumented API, but a gap in the gem's own verification logic.

### Recommendation
Bind the `shop` (and ideally `topic`, `webhook_id`) header values into the HMAC verification step, or independently verify that the `shop` header matches a shop known to have registered the specific `webhook_id` before dispatching to handlers. At minimum, `Utils::HmacValidator.validate` should be extended (or a new check added in `Registry.process`) to reject requests where the header-derived `shop`/`topic` cannot be cryptographically tied to the signed body, closing the gap between "bytes verified" (raw body) and "bytes acted on" (headers).

### Proof of Concept
1. Attacker installs the target app on their own store `attacker-shop.myshopify.com` and registers for a webhook topic the app exposes (e.g., `orders/create`).
2. Shopify sends the app a legitimately signed webhook: body `B`, headers `X-Shopify-Hmac-Sha256: HMAC(secret, B)`, `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`, `X-Shopify-Topic: orders/create`.
3. Attacker captures this request (body `B` + valid HMAC) and re-sends it to the app's webhook controller endpoint, only replacing the header `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new` parses the new headers; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes `HMAC(secret, B)` — identical to before — and returns `true`.
5. `Registry.process` invokes the app's handler with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", topic: "orders/create", body: parsed(B), ...)`, causing the app to process attacker-controlled data as though it originated from `victim-shop.myshopify.com`.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L16-33)
```ruby
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
