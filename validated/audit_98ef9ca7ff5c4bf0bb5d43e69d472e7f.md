### Title
Webhook `shop` (tenant identity) is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb](lib/shopify_api/webhooks/request.rb))

### Summary
`ShopifyAPI::Webhooks::Request` computes the HMAC signature over the raw body only, while the `shop` (tenant identity) is read from an HTTP header that is never included in the signed bytes. `ShopifyAPI::Webhooks::Registry.process` validates only the body's HMAC and then hands the unauthenticated `shop` value straight to the app's handler as if it were verified, breaking the intended binding `hmac_signed_bytes == bytes_the_app_trusts_for_tenant_identity`.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`, and `Request#hmac` reads the `hmac-sha256`/`x-shopify-hmac-sha256` header: [1](#0-0) [2](#0-1) 

`Request#shop` is read from a separate header (`shopify-shop-domain`/`x-shopify-shop-domain`) that is not part of `to_signable_string`: [3](#0-2) 

`HmacValidator.validate` only checks `verifiable_query.hmac` against `verifiable_query.to_signable_string`; it never touches `shop`: [4](#0-3) 

`Registry.process` calls this validator and, once it passes, forwards `request.shop` unmodified into `WebhookMetadata`, which is delivered to the app's `WebhookHandler` as the trusted tenant identifier: [5](#0-4) [6](#0-5) 

Because a single app's `client_secret` is shared across every shop that installs the app, the HMAC computed over the body is identical regardless of which shop the event belongs to — the signature carries no shop-specific binding. The gem's own documentation instructs apps to use `data.shop` as the tenant key to route/store webhook data (e.g. `perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)`): [7](#0-6) 

This is exactly the "field acted on but not covered by the HMAC" pattern: the equality the app relies on is `verified(raw_body) == trusted(shop)`, but the gem only proves `verified(raw_body)`; `shop` is accepted unauthenticated.

### Impact Explanation
An attacker who legitimately installs the same app on their own shop (an unprivileged internet user with respect to any other tenant) receives genuine, correctly-HMAC-signed webhooks from Shopify for their own store. Because the signature covers only the JSON body and not the `shop-domain` header, the attacker can replay that exact body+HMAC pair to the app's public webhook endpoint while substituting the `X-Shopify-Shop-Domain` header with a victim shop's domain. `Utils::HmacValidator.validate` will still return `true` since it only checks the body bytes, and `Registry.process` will dispatch the payload to the handler labeled as coming from the victim shop. Any app that uses `data.shop` (as the docs recommend) to resolve which tenant's records to update, or to determine trust boundaries for downstream logic, is now cross-tenant compromised: forged commerce data can be attributed to and injected into a victim merchant's account state within the app.

### Likelihood Explanation
Exploitation requires only: (1) creating a normal, unprivileged trial/development shop and installing the target app to receive real signed webhooks (a standard, permitted action), and (2) replaying the captured body/HMAC to the same webhook endpoint with a modified shop header — no possession of `client_secret`, tokens, or any elevated access is required. This is well within reach of a normal internet user and does not depend on the host application ignoring documented behavior — the gem's own doc example (`data.shop`) demonstrates the expected (but unsafe) trust pattern.

### Recommendation
Extend `Utils::VerifiableQuery`/`Webhooks::Request#to_signable_string` (or add a dedicated check in `HmacValidator`/`Registry.process`) to bind the `shop-domain` (and ideally `topic`/`webhook_id`) header into what is authenticated before it is exposed via `WebhookMetadata`, or explicitly document that `shop` is unauthenticated header data and must be cross-checked by the host app against a known, previously-authorized shop before being trusted as a tenant key.

### Proof of Concept
1. Install the vulnerable app on attacker-controlled shop `attacker.myshopify.com`; trigger an event (e.g. `orders/create`) so Shopify sends a legitimately signed webhook: body `B`, header `X-Shopify-Hmac-Sha256: H` (valid HMAC of `B` with the app's `client_secret`), header `X-Shopify-Shop-Domain: attacker.myshopify.com`.
2. Replay the same request to the app's webhook endpoint, but replace the `X-Shopify-Shop-Domain` header with `victim.myshopify.com`, keeping body `B` and HMAC `H` unchanged.
3. `ShopifyAPI::Webhooks::Request.new` parses this into an object where `hmac` and `to_signable_string` are unaffected by the header swap.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes HMAC over `B` and compares to `H` — passes, since `shop` was never part of the signed bytes: [8](#0-7) 
5. The handler receives `WebhookMetadata.new(..., shop: "victim.myshopify.com", body: ...)` and the host app processes/stores attacker-controlled data under the victim shop's identity.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-13)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end
```

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

**File:** docs/usage/webhooks.md (L24-27)
```markdown
    def handle(data:)
      puts "Received webhook! topic: #{data.topic} shop: #{data.shop} body: #{data.body} webhook_id: #{data.webhook_id} api_version: #{data.api_version}"
      perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)
    end
```
