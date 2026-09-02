### Title
Webhook `shop`, `topic`, and `webhook_id` headers are trusted for tenant identity but are not covered by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
### Finding Description
`ShopifyAPI::Webhooks::Request` exposes `shop`, `topic`, `api_version`, and `webhook_id` as plain accessors read straight from HTTP headers, while the HMAC signature that `Registry.process` validates is computed only over the raw request body: [1](#0-0) [2](#0-1) 

`Utils::HmacValidator.validate` (invoked as the sole authenticity check in `Registry.process`) recomputes an HMAC over `verifiable_query.to_signable_string` (the raw body) and compares it to the `hmac` accessor (parsed from the `hmac-sha256` header) — it never incorporates `shop`, `topic`, or `webhook_id`: [3](#0-2) 

`Registry.process` performs exactly this single check and then forwards `request.shop` (plus `topic`/`webhook_id`) straight into `WebhookMetadata`, which the host application's handler treats as the authenticated tenant identity for the webhook: [4](#0-3) 

The binding the library implicitly claims to provide is:
`HMAC_valid(raw_body) == true` ⟺ `(shop, topic, webhook_id, raw_body)` all originated from Shopify for that shop.

But the actual binding enforced is only:
`HMAC(secret, raw_body) == received_hmac`

The `shop-domain`, `topic`, and `webhook-id` headers are not part of the signable string, so they are effectively unauthenticated input with respect to the signature check.

### Impact Explanation
Any party who can obtain one genuine `(raw_body, hmac)` pair for a topic (e.g., by installing the app on their own store and capturing a webhook Shopify sends them, which is available to any unprivileged merchant/user of the app, no `api_secret_key` needed) can replay that exact body/HMAC pair to the app's webhook endpoint while substituting the `x-shopify-shop-domain` (and/or `x-shopify-topic`, `x-shopify-webhook-id`) header with a different, victim shop's domain. `HmacValidator.validate` still passes because it only checks the body signature, and `Registry.process` will hand the forged `shop` value to the application's webhook handler as if Shopify itself asserted that identity. If the host application (as documented/intended by this library's API) uses `WebhookMetadata#shop` to select the tenant record to update (a normal and expected usage pattern for `shop/redact`, `customers/redact`, `orders/*`, etc.), the attacker can inject fabricated webhook payloads that are processed under another merchant's tenant — a cross-tenant data-integrity/access violation stemming directly from this gem's own verification logic.

### Likelihood Explanation
Requires no privileged credentials, no `api_secret_key`, and no TLS interception — only a single legitimate webhook capture from any shop that installed the app (the attacker's own store) and the ability to POST to the app's public webhook endpoint with arbitrary headers, which is standard unprivileged internet access.

### Recommendation
Include `shop`, `topic`, and `webhook_id` in the signable string validated by `HmacValidator`, or otherwise cryptographically bind them to the HMAC (e.g., derive/validate `shop` only from a value that is itself covered by the signature) rather than trusting header values that sit outside the HMAC-protected body.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker.myshopify.com` and receives a legitimate webhook, capturing `raw_body` and the `x-shopify-hmac-sha256` header value.
2. Attacker sends a POST to the app's webhook endpoint with the same `raw_body` and `x-shopify-hmac-sha256`, but sets `x-shopify-shop-domain: victim.myshopify.com` (and optionally a different `x-shopify-topic`).
3. `ShopifyAPI::Webhooks::Request` parses `shop` as `victim.myshopify.com`; `Utils::HmacValidator.validate` succeeds because it only checks `HMAC(secret, raw_body)`, per [5](#0-4) .
4. `Registry.process` calls the registered handler with `shop: "victim.myshopify.com"` and the attacker-controlled body, per [4](#0-3) , causing the host application to act on the victim tenant using attacker-supplied data.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-23)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end

      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

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
